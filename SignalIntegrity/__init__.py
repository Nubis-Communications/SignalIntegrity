"""@namespace SignalIntegrity
Signal Integrity Tools"""
import SystemDescriptions as sd
import Conversions as cvt
import Devices as dev
import SParameters as sp
import Splines as spl
import Parsers as p
import SubCircuits as sub
import Helpers as helper
import Symbolic as sy
import ImpedanceProfile as ip
import ChirpZTransform as czt
import TimeDomain as td
import FrequencyDomain as fd
from PySIException import *
import Wavelets as wl
from Rat import *
import Measurement as m
import Test as test
import Fit as fit