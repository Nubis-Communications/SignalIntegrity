import numpy as np
import matplotlib.pyplot as plt
import json

def CalcSNR(Vo_clk, noise):
    #Takes in clock data, assumes that clock data is reasonably well equalized and scaled (don't try too hard on that for now since thats the output of my stuff)
    Vo_clk = np.array(Vo_clk)
    data_00 = Vo_clk[Vo_clk < -0.66]
    data_01 = Vo_clk[np.logical_and(Vo_clk > -0.66, Vo_clk < 0)]
    data_10 = Vo_clk[np.logical_and(Vo_clk > 0, Vo_clk < 0.66)]
    data_11 = Vo_clk[Vo_clk > 0.66]

    avg_power = 10*np.log10(1/4*(np.mean(data_00)**2 + np.mean(data_01)**2 + np.mean(data_11)**2 + np.mean(data_10)**2))
    isi_data_00 = np.mean(np.square(data_00 - np.mean(data_00)))
    isi_data_01 = np.mean(np.square(data_01 - np.mean(data_01)))
    isi_data_10 = np.mean(np.square(data_10 - np.mean(data_10)))
    isi_data_11 = np.mean(np.square(data_11 - np.mean(data_11)))

    isi_noise = 10*np.log10(1/4*(isi_data_00 + isi_data_01 + isi_data_10 + isi_data_11))

    noise_noise = 10*np.log10(np.mean(np.square(noise - np.mean(noise))))

    SNR = avg_power - noise_noise
    SDR = avg_power - isi_noise
    SNDR = avg_power - 10*np.log10(10**(isi_noise/10) + 10**(noise_noise/10))

    args = {}
    args["SNR"] = SNR
    args["SDR"] = SDR
    args["SNDR"] = SNDR
    return args

def CalcErrorVector(Vo_clk):
    Vo_clk = np.array(Vo_clk)
    data_00 = Vo_clk[Vo_clk < -0.66]
    data_01 = Vo_clk[np.logical_and(Vo_clk > -0.66, Vo_clk < 0)]
    data_10 = Vo_clk[np.logical_and(Vo_clk > 0, Vo_clk < 0.66)]
    data_11 = Vo_clk[Vo_clk > 0.66]

    errors = np.zeros(Vo_clk.shape)
    errors[Vo_clk < -0.66] = Vo_clk[Vo_clk < -0.66] - np.mean(Vo_clk[Vo_clk < -0.66])
    errors[np.logical_and(Vo_clk > -0.66, Vo_clk < 0)] = Vo_clk[np.logical_and(Vo_clk > -0.66, Vo_clk < 0)] - np.mean(Vo_clk[np.logical_and(Vo_clk > -0.66, Vo_clk < 0)])
    errors[np.logical_and(Vo_clk > -0.66, Vo_clk < 0)] = Vo_clk[np.logical_and(Vo_clk > -0.66, Vo_clk < 0)] - np.mean(Vo_clk[np.logical_and(Vo_clk > -0.66, Vo_clk < 0)])
    errors[np.logical_and(Vo_clk > 0, Vo_clk < 0.66)] = Vo_clk[np.logical_and(Vo_clk > 0, Vo_clk < 0.66)] - np.mean(Vo_clk[np.logical_and(Vo_clk > 0, Vo_clk < 0.66)])
    errors[Vo_clk > 0.66] = Vo_clk[Vo_clk > 0.66] - np.mean(Vo_clk[Vo_clk > 0.66])

    return errors

if __name__ == "__main__":

    json_fn = "C:\\Users\\danie\\Documents\\TIA_BW\\MultiLossSweep_FineOma\\TiaBWSimulationWPD_OMA_-4_Ind_50_Use_DFE_False_L_10\\Output.json"

    with open(json_fn) as json_file:
        data = json.load(json_file)

    Vo_clk = data['RX_Tuneup_Params']['VoWfdec_eq']
    ideal_data = data['RX_Tuneup_Params']['ideal_data']
    noise = data['RX_Tuneup_Params']['Noise_Eq']

    CalcSNR(Vo_clk, noise)
    plt.hist(Vo_clk)
    plt.show()

