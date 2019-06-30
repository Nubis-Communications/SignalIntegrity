def EqualizerFit(project,waveform,delay,bitrate):
    import SignalIntegrity.App as siapp
    import SignalIntegrity.Lib as si
    app=siapp.SignalIntegrityAppHeadless()
    app.OpenProjectFile(project)
    (_,outputWaveformLabels,_,outputWaveformList)=app.Simulate()
    prbswf=outputWaveformList[outputWaveformLabels.index(waveform)]
    H=prbswf.td.H; ui=1./bitrate
    dH=int(H/ui)*ui-delay+ui; lastTime=prbswf.Times()[-1]; dK=int((lastTime-ui-dH)/ui)
    decwftd=si.td.wf.TimeDescriptor(dH,dK,bitrate)
    decwf=si.td.wf.Waveform(decwftd,[prbswf.Measure(t) for t in decwftd.Times()])
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    fitter=EqualizerFitter()
    fitter.Initialize(decwf,[-0.25,-0.1667/2.,0.1667/2.,0.25],1,1)
    fitter.Solve()
    print(fitter.Results())
