import SignalIntegrity.Lib as si

symbolic = si.sd.Symbolic()
symbolic.DocStart()
symbolic._AddEq('\\mathbf{S}='+symbolic._LaTeXMatrix(si.sy.SeriesZ('Z')))
symbolic.DocEnd()
symbolic.WriteToFile('Symbolic.tex')
