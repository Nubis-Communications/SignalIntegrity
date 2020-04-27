def EyePattern(project,waveform,delay,bitrate):
    import numpy as np
    import SignalIntegrity.App as siapp
    app=siapp.SignalIntegrityAppHeadless()
    app.OpenProjectFile(project)
    (_,outputWaveformLabels,_,outputWaveformList)=app.Simulate()
    prbswf=outputWaveformList[outputWaveformLabels.index(waveform)]
    ui=1./bitrate; times=prbswf.Times()
    timesInBit=[((t-delay)/3./ui-int((t-delay)/3./ui))*3.*ui for t in times]
    from PIL import Image
    R=400; C=600
    EyeWfCols=[int(t/3./ui*C) for t in timesInBit]
    EyeWfRows=[int((v+0.3)/0.6*R) for v in prbswf.Values()]
    bitmap=[[0 for c in range(C)] for _ in range(R)]
    for i in range(len(EyeWfRows)):
        bitmap[EyeWfRows[i]][EyeWfCols[i]]=bitmap[EyeWfRows[i]][EyeWfCols[i]]+1
    maxValue=(max([max(v) for v in bitmap]))
    bitmap=[[int((maxValue - float(bitmap[r][c]))/maxValue*255.0)
             for c in range(C)] for r in range(R)]
    img=Image.fromarray(np.squeeze(np.asarray(np.array(bitmap))).astype(np.uint8))
    img.save(waveform+'.png')
