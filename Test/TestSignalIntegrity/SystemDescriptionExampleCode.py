from __future__ import print_function
import SignalIntegrity.Lib as si
sd = si.sd.SystemDescription()
sd.AddDevice('L', 2)  # add two-port left device
sd.AddDevice('R', 2)  # add two-port right device
sd.AddPort('L', 1, 1)  # add a port at port 1 of left device
sd.AddPort('R', 2, 2)  # add a port at port 2 of right device
sd.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
sd.Print()  # print the system description
spc = si.sd.SystemSParameters(sd)
n = spc.NodeVector()  # get the node vector
m = spc.StimulusVector()  # get the stimulus vector
W = spc.WeightsMatrix()  # get the weights matrix
# print out the vectors and matrices
print(('{0:' + str(5 * len(n)) + '}').format('Weights Matrix'), end=' ')
print('| {0:4}'.format('n'), end=' ')
print('| {0:4} |'.format('m'))
print('----------------------------------------------')
for r in range(len(W)):
    for c in range(len(W[r])):
        print('{0:4}'.format(str(W[r][c])), end=' ')
    print(' | {0:4}'.format(n[r]), end=' ')
    print('| {0:4} |'.format(m[r]))
print('----------------------------------------------')
