from Gaudi.Configuration import *
from Configurables import MarlinProcessorWrapper

from constants import *

######################################
#### Defines the following processor:
# VXDBarrelDigitiser
# VXDEndcapDigitiser
# InnerPlanarDigiProcessor
# InnerEndcapPlanarDigiProcessor
# OuterPlanarDigiProcessor
# OuterEndcapPlanarDigiProcessor
# DDCaloDigi
# DDSimpleMuonDigi
######################################


VXDBarrelDigitiser = MarlinProcessorWrapper("VXDBarrelDigitiser")
VXDBarrelDigitiser.OutputLevel = INFO
VXDBarrelDigitiser.ProcessorType = "DDPlanarDigiProcessor"
VXDBarrelDigitiser.Parameters = {
                                 "CorrectTimesForPropagation": ["true"],
                                 "IsStrip": ["false"],
                                 "ResolutionT": ["0.03"],
                                 "ResolutionU": ["0.005"],
                                 "ResolutionV": ["0.005"],
                                 "SimTrackHitCollectionName": [ VXDB_s],
                                 "SimTrkHitRelCollection": [ VXDB_r ],
                                 "SubDetectorName": ["Vertex"],
                                 "TimeWindowMax": ["0.15"],
                                 "TimeWindowMin": ["-0.09"],
                                 "TrackerHitCollectionName": [ VXDB_d ],
                                 "UseTimeWindow": ["true"]
                                 }

VXDEndcapDigitiser = MarlinProcessorWrapper("VXDEndcapDigitiser")
VXDEndcapDigitiser.OutputLevel = INFO
VXDEndcapDigitiser.ProcessorType = "DDPlanarDigiProcessor"
VXDEndcapDigitiser.Parameters = {
                                 "CorrectTimesForPropagation": ["true"],
                                 "IsStrip": ["false"],
                                 "ResolutionT": ["0.03"],
                                 "ResolutionU": ["0.005"],
                                 "ResolutionV": ["0.005"],
                                 "SimTrackHitCollectionName": [ VXDE_s],
                                 "SimTrkHitRelCollection": [ VXDE_r ],
                                 "SubDetectorName": ["Vertex"],
                                 "TimeWindowMax": ["0.15"],
                                 "TimeWindowMin": ["-0.09"],
                                 "TrackerHitCollectionName": [ VXDE_d ],
                                 "UseTimeWindow": ["true"]
                                 }

InnerPlanarDigiProcessor = MarlinProcessorWrapper("InnerPlanarDigiProcessor")
InnerPlanarDigiProcessor.OutputLevel = INFO
InnerPlanarDigiProcessor.ProcessorType = "DDPlanarDigiProcessor"
InnerPlanarDigiProcessor.Parameters = {
                                       "CorrectTimesForPropagation": ["true"],
                                       "IsStrip": ["false"],
                                       "ResolutionT": ["0.06"],
                                       "ResolutionU": ["0.007"],
                                       "ResolutionV": ["0.090"],
                                       "SimTrackHitCollectionName": [ ITDB_s ],
                                       "SimTrkHitRelCollection": [ ITDB_r ],
                                       "SubDetectorName": ["InnerTrackers"],
                                       "TimeWindowMax": ["0.3"],
                                       "TimeWindowMin": ["-0.18"],
                                       "TrackerHitCollectionName": [ ITDB_d ],
                                       "UseTimeWindow": ["true"]
                                       }

InnerEndcapPlanarDigiProcessor = MarlinProcessorWrapper("InnerEndcapPlanarDigiProcessor")
InnerEndcapPlanarDigiProcessor.OutputLevel = INFO
InnerEndcapPlanarDigiProcessor.ProcessorType = "DDPlanarDigiProcessor"
InnerEndcapPlanarDigiProcessor.Parameters = {
                                             "CorrectTimesForPropagation": ["true"],
                                             "IsStrip": ["false"],
                                             "ResolutionT": ["0.06"],
                                             "ResolutionU": ["0.007"],
                                             "ResolutionV": ["0.090"],
                                             "SimTrackHitCollectionName": [ ITDE_s ],
                                             "SimTrkHitRelCollection": [ ITDE_r ],
                                             "SubDetectorName": ["InnerTrackers"],
                                             "TimeWindowMax": ["0.3"],
                                             "TimeWindowMin": ["-0.18"],
                                             "TrackerHitCollectionName": [ ITDE_d ],
                                             "UseTimeWindow": ["true"]
                                             }

OuterPlanarDigiProcessor = MarlinProcessorWrapper("OuterPlanarDigiProcessor")
OuterPlanarDigiProcessor.OutputLevel = INFO
OuterPlanarDigiProcessor.ProcessorType = "DDPlanarDigiProcessor"
OuterPlanarDigiProcessor.Parameters = {
                                       "CorrectTimesForPropagation": ["true"],
                                       "IsStrip": ["false"],
                                       "ResolutionT": ["0.06"],
                                       "ResolutionU": ["0.007"],
                                       "ResolutionV": ["0.090"],
                                       "SimTrackHitCollectionName": [ OTDB_s ],
                                       "SimTrkHitRelCollection": [ OTDB_r ],
                                       "SubDetectorName": ["OuterTrackers"],
                                       "TimeWindowMax": ["0.3"],
                                       "TimeWindowMin": ["-0.18"],
                                       "TrackerHitCollectionName": [ OTDB_d ],
                                       "UseTimeWindow": ["true"]
                                       }

OuterEndcapPlanarDigiProcessor = MarlinProcessorWrapper("OuterEndcapPlanarDigiProcessor")
OuterEndcapPlanarDigiProcessor.OutputLevel = INFO
OuterEndcapPlanarDigiProcessor.ProcessorType = "DDPlanarDigiProcessor"
OuterEndcapPlanarDigiProcessor.Parameters = {
                                             "CorrectTimesForPropagation": ["true"],
                                             "IsStrip": ["false"],
                                             "ResolutionT": ["0.06"],
                                             "ResolutionU": ["0.007"],
                                             "ResolutionV": ["0.090"],
                                             "SimTrackHitCollectionName": [ OTDE_s ],
                                             "SimTrkHitRelCollection": [ OTDE_r ],
                                             "SubDetectorName": ["OuterTrackers"],
                                             "TimeWindowMax": ["0.3"],
                                             "TimeWindowMin": ["-0.18"],
                                             "TrackerHitCollectionName": [ OTDE_d ],
                                             "UseTimeWindow": ["true"]
                                             }

CaloDigiDefaultParam = {
                           "CalibECALMIP": ["33.6"],
                           "CalibHCALMIP": ["0.0001"],
                           "CalibrECAL": ["1.3", "1.3"],
                           "CalibrHCALBarrel": ["49.2031079063"],
                           "CalibrHCALEndcap": ["53.6263377733"],
                           "CalibrHCALOther": ["62.2125698179"],
                           "CrilinBarrelThreshold": ["50.", "50.", "50.", "20.", "20.", "20.", "10.", "10.", "10.", "5.", "10.", "10.", "5.", "5.", "5.", "5.", "5.", "5."],
                           "CrilinBarrelTimeMax": ["0.2", "0.12",  "0.1",  "0.2", "0.12", "0.1", "0.15", "0.12", "0.1",  "0.2", "0.15", "0.2", "0.25", "0.2", "0.25", "0.3", "0.3", "0.3"],
                           "CrilinBarrelTimeMin": ["-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1"],
                           "CrilinEndcapThreshold": ["100.", "70.", "70.", "50.", "40.", "30.", "40.", "20.", "20.", "25.", "25.", "10.", "20.", "10.", "10.", "20.", "10.", "10."],
                           "CrilinEndcapTimeMax": ["0.3", "0.15", "0.2",  "0.2", "0.25", "0.3",  "0.2", "0.25", "0.3", "0.15", "0.2", "0.3",  "0.15",  "0.2", "0.3", "0.15", "0.2", "0.3"],
                           "CrilinEndcapTimeMin": ["-0.05", "-0.05", "-0.05",  "-0.06", "-0.06", "-0.06",  "-0.06", "-0.06", "-0.06",  "-0.06", "-0.06", "-0.06",  "-0.06", "-0.06", "-0.06",  "-0.06", "-0.06", "-0.06" ],
                           "CrilinPreselectionTimeCut": ["0.5"],
                           "SignalDecayConstant": ["10."],
                           "SignalTriggerThresholdsBarrel": ["50.", "20.", "10.", "5.", "5.", "5."],
                           "SignalTriggerThresholdsEndcap" : ["70.", "20.", "20.", "10.", "10.", "10."],
                           "TriggerBlindTime": ["-0.1"],
                           "ECALBarrelTimeWindowMax": ["25"],
                           "ECALCollections": [ ECB_s, ECE_s ],
                           "ECALCorrectTimesForPropagation": ["1"],
                           "ECALDeltaTimeHitResolution": ["10"],
                           "ECALEndcapCorrectionFactor": ["1.0"],
                           "ECALEndcapTimeWindowMax": ["25"],
                           "ECALGapCorrection": ["0"],
                           "ECALGapCorrectionFactor": ["1"],
                           "ECALLayers": ["41", "100"],
                           "ECALModuleGapCorrectionFactor": ["0.0"],
                           "ECALOutputCollection0": [ ECB_d ],
                           "ECALOutputCollection1": [ ECE_d ],
                           "ECALSimpleTimingCut": ["true"],
                           "ECALThreshold": ["0.002"],
                           "ECALThresholdUnit": ["GeV"],
                           "ECALTimeResolution": ["10"],
                           "ECALTimeWindowMin": ["-1"],
                           "ECAL_PPD_N_Pixels": ["10000"],
                           "ECAL_PPD_N_Pixels_uncertainty": ["0.05"],
                           "ECAL_PPD_PE_per_MIP": ["7"],
                           "ECAL_apply_realistic_digi": ["0"],
                           "ECAL_deadCellRate": ["0"],
                           "ECAL_deadCell_memorise": ["false"],
                           "ECAL_default_layerConfig": ["000000000000000"],
                           "ECAL_elec_noise_mips": ["0"],
                           "ECAL_maxDynamicRange_MIP": ["2500"],
                           "ECAL_miscalibration_correl": ["0"],
                           "ECAL_miscalibration_uncorrel": ["0"],
                           "ECAL_miscalibration_uncorrel_memorise": ["false"],
                           "ECAL_pixel_spread": ["0.05"],
                           "ECAL_strip_absorbtionLength": ["1e+06"],
                           "ECAL_use_Crilin": ["true"],
                           "HCALBarrelTimeWindowMax": ["25."],
                           "HCALCollections": [ HCB_s, HCE_s ],
                           "HCALCorrectTimesForPropagation": ["1"],
                           "HCALDeltaTimeHitResolution": ["10"],
                           "HCALEndcapCorrectionFactor": ["1.000"],
                           "HCALEndcapTimeWindowMax": ["25."],
                           "HCALGapCorrection": ["0"],
                           "HCALLayers": ["100"],
                           "HCALModuleGapCorrectionFactor": ["0.5"],
                           "HCALOutputCollection0": [ HCB_d ],
                           "HCALOutputCollection1": [ HCE_d ],
                           "HCALSimpleTimingCut": ["true"],
                           "HCALThreshold": ["0.002"],
                           "HCALThresholdUnit": ["GeV"],
                           "HCALTimeResolution": ["10"],
                           "HCALTimeWindowMin": ["-1"],
                           "HCAL_PPD_N_Pixels": ["400"],
                           "HCAL_PPD_N_Pixels_uncertainty": ["0.05"],
                           "HCAL_PPD_PE_per_MIP": ["10"],
                           "HCAL_apply_realistic_digi": ["0"],
                           "HCAL_deadCellRate": ["0"],
                           "HCAL_deadCell_memorise": ["false"],
                           "HCAL_elec_noise_mips": ["0"],
                           "HCAL_maxDynamicRange_MIP": ["200"],
                           "HCAL_miscalibration_correl": ["0"],
                           "HCAL_miscalibration_uncorrel": ["0"],
                           "HCAL_miscalibration_uncorrel_memorise": ["false"],
                           "HCAL_pixel_spread": ["0"],
                           "Histograms": ["0"],
                           "IfDigitalEcal": ["0"],
                           "IfDigitalHcal": ["0"],
                           "MapsEcalCorrection": ["0"],
                           "RelationOutputCollection": [ CALO_r ],
                           "RootFile": ["Digi_SiW.root"],
                           "StripEcal_default_nVirtualCells": ["9"],
                           "UseEcalTiming": ["1"],
                           "UseHcalTiming": ["1"],
                           "energyPerEHpair": ["3.6"]
                           }

DDCaloDigi = MarlinProcessorWrapper("DDCaloDigi")
DDCaloDigi.OutputLevel = INFO
DDCaloDigi.ProcessorType = "DDCaloDigi_BIB"
DDCaloDigi.Parameters = CaloDigiDefaultParam

DDSimpleMuonDigi = MarlinProcessorWrapper("DDSimpleMuonDigi")
DDSimpleMuonDigi.OutputLevel = INFO
DDSimpleMuonDigi.ProcessorType = "DDSimpleMuonDigi"
DDSimpleMuonDigi.Parameters = {
                                 "CalibrMUON": ["70.1"],
                                 "MUONCollections": [ YDB_s, YDE_s ],
                                 "MUONOutputCollection": [ MuD_d ],
                                 "MaxHitEnergyMUON": ["2.0"],
                                 "MuonThreshold": ["1e-06"],
                                 "RelationOutputCollection": [ MUON_r ]
                                 }

