"""
Results.py
"""
# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import base64
import io
import math

import numpy as np

VIEWS=('time','content','density')
SPARAMETER_TIME_VIEWS=('impulse','step','impedance')
IMPEDANCE_LIMIT=3000.

def Decimate(x,y,maxPoints):
    """min/max envelope decimation that keeps every peak visible
    @return (x,y) numpy arrays with at most about maxPoints points"""
    n=len(y)
    if maxPoints is None or n<=maxPoints or maxPoints<4:
        return x,y
    buckets=maxPoints//2
    edges=np.linspace(0,n,buckets+1).astype(int)
    xs=np.empty(2*buckets); ys=np.empty(2*buckets)
    for b in range(buckets):
        lo,hi=edges[b],max(edges[b+1],edges[b]+1)
        segment=y[lo:hi]
        imin=lo+int(np.argmin(segment)); imax=lo+int(np.argmax(segment))
        first,second=(imin,imax) if imin<=imax else (imax,imin)
        xs[2*b],ys[2*b]=x[first],y[first]
        xs[2*b+1],ys[2*b+1]=x[second],y[second]
    return xs,ys

def _List(a):
    return [None if not math.isfinite(v) else float(v) for v in a]

class ResultData(object):
    """the result of a calculation or a device view, holding the original SignalIntegrity objects.

    waveforms is a list of (name, Waveform or float for DC), sparameters a list of (name, SParameters)
    and eyes a list of (name, PIL image).  The order and content of waveforms matches what the tk
    simulator dialog displays."""
    def __init__(self,kind,title='',endFrequency=None):
        self.kind=kind
        self.title=title
        self.endFrequency=endFrequency
        self.waveforms=[]
        self.sparameters=[]
        self.eyes=[]
        self.noise=None
        self._cache={}
    @classmethod
    def FromHeadless(cls,result,title='',endFrequency=None):
        data=cls(result['type'],title,endFrequency)
        if result['type'] in ('simulation','virtual probe'):
            names=list(result.get('output waveform labels',[]))
            waveforms=list(result.get('output waveforms',[]))
            # 'other waveforms' repeats the extra output waveforms and adds the shown processor sources
            for name,wf in zip(result.get('other waveform labels',[]),result.get('other waveforms',[])):
                if name not in names:
                    names.append(name); waveforms.append(wf)
            data.waveforms=[(n,wf) for n,wf in zip(names,waveforms) if wf is not None]
            for name,eye in zip(result.get('eye diagram labels',[]),result.get('eye diagrams',[])):
                if getattr(eye,'img',None) is not None:
                    data.eyes.append((name,eye.img))
            noise=result.get('noise')
            if isinstance(noise,dict) and noise.get('noise_display_output_names'):
                data.noise=noise
        elif result['type']=='s-parameters':
            import os
            data.sparameters=[(os.path.basename(result['file names']),result['s-parameters'])]
        elif result['type']=='de-embed':
            data.sparameters=list(zip(result['unknown names'],result['s-parameters']))
        return data
    @staticmethod
    def IsDC(wf):
        return isinstance(wf,(int,float))
    def _Time(self,i):
        key=('time',i)
        if key not in self._cache:
            wf=self.waveforms[i][1]
            self._cache[key]=(np.asarray(wf.Times(),dtype=float),np.asarray(wf.Values(),dtype=float).real)
        return self._cache[key]
    def _Frequency(self,i,density):
        key=('density' if density else 'content',i)
        if key not in self._cache:
            wf=self.waveforms[i][1]
            fc=wf.FrequencyContent()
            if self.endFrequency is not None:
                fc=fc.LimitEndFrequency(self.endFrequency)
            self._cache[key]=(np.asarray(fc.Frequencies(),dtype=float),
                              np.asarray(fc.Values('dBmPerHz' if density else 'dBm'),dtype=float))
        return self._cache[key]
    def Arrays(self,i,view='time'):
        """@return (x,y) numpy arrays of waveform i in a view, or None for a DC waveform"""
        if self.IsDC(self.waveforms[i][1]):
            return None
        if view=='time':
            return self._Time(i)
        return self._Frequency(i,view=='density')
    def AutoscaleLimits(self,view='time',indices=None):
        """x and y limits chosen the way the tk simulator dialog chooses them
        @return [xmin,xmax,ymin,ymax] with None for any limit that can't be determined"""
        indices=range(len(self.waveforms)) if indices is None else indices
        xmin=xmax=ymin=ymax=yStd=None
        for i in indices:
            wf=self.waveforms[i][1]
            if self.IsDC(wf):
                if view=='time':
                    ymin=wf if ymin is None else min(ymin,wf); ymax=wf if ymax is None else max(ymax,wf)
                continue
            x,y=self.Arrays(i,view)
            if len(x)==0:
                continue
            xmin=x[0] if xmin is None else min(xmin,x[0]); xmax=x[-1] if xmax is None else max(xmax,x[-1])
            finite=y[np.isfinite(y)]
            if len(finite)==0:
                continue
            ymin=finite.min() if ymin is None else min(ymin,finite.min())
            ymax=finite.max() if ymax is None else max(ymax,finite.max())
            if view!='time':
                s=finite.mean()-0.5*finite.std()
                yStd=s if yStd is None else min(yStd,s)
        if yStd is not None and ymin is not None:
            ymin=max(ymin,yStd)
        return [None if v is None else float(v) for v in (xmin,xmax,ymin,ymax)]
    def Series(self,view='time',indices=None,xmin=None,xmax=None,maxPoints=None):
        """JSON-serializable plot data, limited to an x range and decimated to maxPoints per trace"""
        if view not in VIEWS:
            raise ValueError('unknown view '+str(view))
        indices=range(len(self.waveforms)) if indices is None else indices
        series=[]
        for i in indices:
            name,wf=self.waveforms[i]
            if self.IsDC(wf):
                series.append({'index':i,'name':name,'dc':float(wf) if view=='time' else None,'x':[],'y':[]})
                continue
            x,y=self.Arrays(i,view)
            lo,hi=0,len(x)
            if xmin is not None:
                lo=max(0,int(np.searchsorted(x,xmin))-1)
            if xmax is not None:
                hi=min(len(x),int(np.searchsorted(x,xmax,side='right'))+1)
            xs,ys=Decimate(x[lo:hi],y[lo:hi],maxPoints)
            series.append({'index':i,'name':name,'dc':None,'x':_List(xs),'y':_List(ys),'total':int(hi-lo)})
        return {'view':view,'series':series,'autoscale':self.AutoscaleLimits(view,indices)}
    def WaveformInfo(self):
        info=[]
        for i,(name,wf) in enumerate(self.waveforms):
            if self.IsDC(wf):
                info.append({'index':i,'name':name,'dc':float(wf)})
            else:
                info.append({'index':i,'name':name,'dc':None,'points':int(wf.td.K),'start':float(wf.td.H),'sampleRate':float(wf.td.Fs)})
        return info
    @staticmethod
    def SParametersData(name,sp):
        P=sp.m_P
        traces=[]
        for o in range(1,P+1):
            for i in range(1,P+1):
                fr=sp.FrequencyResponse(o,i)
                traces.append({'name':'S'+str(o)+str(i),'to':o,'from':i,
                               'dB':_List(fr.Values('dB')),'deg':_List(fr.Values('deg'))})
        return {'name':name,'ports':P,'frequencies':[float(f) for f in sp.f()],'traces':traces}
    def SParameterTime(self,index,view,maxPoints=None):
        """the tk S-parameter viewer's time-domain views of sparameters[index]: 'impulse' and 'step'
        responses of every Sij, or 'impedance' (TDR) of every reflection Sii, with x in seconds
        (round-trip time halved for impedance) and y unitless or in ohms
        @return {name,view,traces:[{name,to,from,x,y}]}"""
        import SignalIntegrity.Lib as si
        if view not in SPARAMETER_TIME_VIEWS:
            raise ValueError('unknown s-parameter view '+str(view))
        name,sp=self.sparameters[index]
        key=('sp',index,view)
        if key not in self._cache:
            Z0=float(np.real(getattr(sp,'m_Z0',50.)))
            traces=[]
            for o in range(1,sp.m_P+1):
                for i in range(1,sp.m_P+1):
                    if view=='impedance' and o!=i:
                        continue
                    ir=sp.FrequencyResponse(o,i).ImpulseResponse()
                    if ir is None:
                        raise ValueError('time-domain views need evenly spaced frequencies starting at 0 Hz')
                    if view=='impulse':
                        x,y=np.asarray(ir.Times(),dtype=float),np.asarray(ir.Values(),dtype=float).real
                    else:
                        fir=ir.FirFilter()
                        step=si.td.wf.StepWaveform(ir.td/fir.FilterDescriptor())*fir
                        x,y=np.asarray(step.Times(),dtype=float),np.asarray(step.Values(),dtype=float).real
                        if view=='impedance':
                            with np.errstate(divide='ignore',invalid='ignore'):
                                z=Z0*(1.+y)/(1.-y)
                            y=np.where((1.-y)<=1e-6,IMPEDANCE_LIMIT,np.minimum(z,IMPEDANCE_LIMIT))
                            x=x/2.
                    traces.append({'name':'S'+str(o)+str(i),'to':o,'from':i,'x':x,'y':y})
            self._cache[key]=traces
        out=[]
        for t in self._cache[key]:
            xs,ys=Decimate(t['x'],t['y'],maxPoints)
            out.append({'name':t['name'],'to':t['to'],'from':t['from'],'x':_List(xs),'y':_List(ys)})
        return {'name':name,'view':view,'traces':out}
    # ---- statistical noise (the tk Statistical Noise and Noise Measurements dialogs)
    def _NoiseNames(self):
        return list(self.noise['noise_display_output_names']) if self.noise else []
    def NoiseInfo(self):
        """@return per displayed output: {index,name,type,rms,dBm,rmsPerRootHz,dBmPerHz,SNR,SalzSNR,
        contributions:[{name,rms,dBm,SNR}]} as the tk noise measurements dialog shows them"""
        info=[]
        for k,name in enumerate(self._NoiseNames()):
            density=self.noise['output_noise_spectral_density'][name]
            spectrum=density['spectrum']
            end=float(spectrum.Frequencies()[-1]) if len(spectrum.Frequencies()) else 0.
            rms=float(density['rms'])
            snr=self.noise.get('signal_to_noise_ratio',{}).get(name,{})
            contributions=self.noise.get('contributions',{}).get(name,{})
            num=lambda v: None if v is None or not math.isfinite(float(v)) else float(v)
            info.append({'index':k,'name':name,'type':density.get('type','voltage'),'rms':num(rms),'dBm':num(density.get('dBm')),
                         'rmsPerRootHz':num(rms/math.sqrt(end)) if end>0 else None,
                         'dBmPerHz':num(density.get('dBm')-10.*math.log10(end)) if end>0 and density.get('dBm') is not None else None,
                         'SNR':num(snr.get('SNR')),'SalzSNR':num(snr.get('SalzSNR')),
                         # a source that does not reach this output has no meaningful dBm or SNR (only the -3000 dBm floor)
                         'contributions':[{'name':source,'rms':num(c.get('rms')),
                                           'dBm':num(c.get('dBm')) if c.get('rms') else None,
                                           'SNR':num(c.get('SNR')) if c.get('rms') else None}
                                          for source,c in contributions.items()]})
        return info
    def NoiseSeries(self,indices=None,maxPoints=None):
        """output noise spectral densities in dBm/Hz versus frequency in Hz
        @return {series:[{index,name,x,y}],autoscale:[xmin,xmax,ymin,ymax]}"""
        names=self._NoiseNames()
        indices=range(len(names)) if indices is None else indices
        series=[]; lo=hi=None
        for k in indices:
            spectrum=self.noise['output_noise_spectral_density'][names[k]]['spectrum']
            x=np.asarray(spectrum.Frequencies(),dtype=float)
            with np.errstate(divide='ignore'):
                y=np.asarray(spectrum.Values('dBm/Hz'),dtype=float)
            finite=y[np.isfinite(y)&(y>-200.)]
            if len(finite):
                lo=finite.min() if lo is None else min(lo,finite.min())
                hi=finite.max() if hi is None else max(hi,finite.max())
            xs,ys=Decimate(x,y,maxPoints)
            series.append({'index':int(k),'name':names[k],'x':_List(xs),'y':_List(ys)})
        xmax=max((s['x'][-1] for s in series if s['x']),default=None)
        return {'series':series,'autoscale':[0. if xmax is not None else None,xmax,
                                             None if lo is None else float(lo-1.),None if hi is None else float(hi+1.)]}
    @staticmethod
    def PngDataUrl(image):
        buffer=io.BytesIO()
        image.save(buffer,format='PNG')
        return 'data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode('ascii')
    def Summary(self):
        """JSON-serializable description; waveform samples are fetched separately with Series"""
        return {'type':self.kind,'title':self.title,
                'waveforms':self.WaveformInfo(),
                'sparameters':[self.SParametersData(n,sp) for n,sp in self.sparameters],
                'eyes':[{'name':n,'image':self.PngDataUrl(img)} for n,img in self.eyes],
                'noise':self.NoiseInfo()}
