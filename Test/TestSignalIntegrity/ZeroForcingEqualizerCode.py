def ZeroForcingEqualizer(project,waveform,bitrate,value,pre,taps):
    import SignalIntegrity.App as siapp; from numpy import array
    from numpy.linalg import pinv
    app=siapp.SignalIntegrityAppHeadless()
    app.OpenProjectFile(project)
    (_,outputWaveformLabels,_,outputWaveformList)=app.Simulate()
    pulsewf=outputWaveformList[outputWaveformLabels.index(waveform)]
    delay=pulsewf.td.TimeOfPoint(pulsewf.Values().index(max(pulsewf.Values())))
    print('delay: '+str(delay))
    H=pulsewf.td.H; ui=1./bitrate
    startTime=delay-(int((delay-H)/ui)-1)*ui
    endTime=delay+(int((pulsewf.Times()[-1]-delay)/ui-1)*ui)
    M=int((endTime-startTime)/ui+0.5); d=int((delay-startTime)/ui+0.5)
    x=[pulsewf.Measure(startTime+m*ui) for m in range(M)]
    X=[[0 if r-c < 0 else x[r-c] for c in range(taps)] for r in range(M)]
    r=[[value] if r == d+pre else [0] for r in range(len(X))]
    a=[v[0] for v in (pinv(array(X)).dot(array(r))).tolist()]
    print('results: '+str(a))
