import os
from Gaudi.Configuration import *

from Configurables import LcioEvent, EventDataSvc, MarlinProcessorWrapper
from k4FWCore.parseArgs import parser

##### Import processors
import sys
sys.path.append('conf')

from digit    import *
from overlay  import *
from tracking import *
from calo     import *
from ntuple   import *
from vertex   import *

### Some predefined variables
GEOFILE      = os.environ.get("MUCOLL_GEO", "")

### Arguments:
# --geo: geometry, default $MUCOLL_GEO
# --overlay: overlay type: ['full', 'trimmed', 'test', 'none'], default: trimmed
# --root: Root filename for AIDA processor, default: aida
# --output: slcio output file, default: Output.slcio
# --nevt: Number of event to process, default all
# --input: signal input file. REQUIRED.

parser.add_argument(
    "--geo",
    help="Compact detector description file",
    type=str,
    default = GEOFILE,
)

parser.add_argument(
    "--overlay",
    help="Which BIB overlay",
    type=str,
    choices=['full', 'trimmed', 'test', 'none'],
    default="trimmed",
)

parser.add_argument(
    "--input",
    help="Signal input file",
    type=str,
    required=True,
)

parser.add_argument(
    "--root",
    help="AIDA output root file",
    type=str,
    default="aida",
)

parser.add_argument(
    "--output",
    help="slcio output file",
    type=str,
    default="Output.slcio"
)

parser.add_argument(
    "--nevt",
    help="Number of events",
    type=int,
    default=-1,
)

the_args = parser.parse_known_args()[0]

algList = []
evtsvc = EventDataSvc()

read = LcioEvent()
read.OutputLevel = INFO
read.Files = [ the_args.input ]
algList.append(read)

########## Processor

DD4hep = MarlinProcessorWrapper("DD4hep")
DD4hep.OutputLevel = INFO
DD4hep.ProcessorType = "InitializeDD4hep"
DD4hep.Parameters = {
    "DD4hepXMLFile": [the_args.geo],
    "EncodingStringParameterName": ["GlobalTrackerReadoutID"]
}

Config = MarlinProcessorWrapper("Config")
Config.OutputLevel = INFO
Config.ProcessorType = "CLICRecoConfig"
Config.Parameters = {
    "VertexUnconstrained": ["OFF"],
    "VertexUnconstrainedChoices": ["ON", "OFF"]
}

AIDA = MarlinProcessorWrapper("AIDA")
AIDA.OutputLevel = INFO
AIDA.ProcessorType = "AIDAProcessor"
AIDA.Parameters = {
    "Compress": ["1"],
    "FileName": [ the_args.root ],
    "FileType": ["root"]
}

EventNumber = MarlinProcessorWrapper("EventNumber")
EventNumber.OutputLevel = INFO
EventNumber.ProcessorType = "Statusmonitor"
EventNumber.Parameters = {
    "HowOften": ["1"]
}


LCIOWriter_all = MarlinProcessorWrapper("LCIOWriter_all")
LCIOWriter_all.OutputLevel = INFO
LCIOWriter_all.ProcessorType = "LCIOOutputProcessor"
LCIOWriter_all.Parameters = {
    "DropCollectionNames": [ "SeedTracks" ],
    "DropCollectionTypes": ['SimCalorimeterHit','SimTrackerHit'],
    "FullSubsetCollections": [],
    "KeepCollectionNames": [],
    "LCIOOutputFile": [ the_args.output ],
    "LCIOWriteMode": ["WRITE_NEW"]
}

#### reduced version
LCIOWriter_light = MarlinProcessorWrapper("LCIOWriter_light")
LCIOWriter_light.OutputLevel = INFO
LCIOWriter_light.ProcessorType = "LCIOOutputProcessor"
LCIOWriter_light.Parameters = {
    "DropCollectionNames": [ "SeedTracks", "AllTracks", 'SiTracks' ],
    "DropCollectionTypes": ['SimCalorimeterHit','SimTrackerHit', 'TrackerHitPlane', 'LCRelation', 'MCParticle'],
    "FullSubsetCollections": ['CaloHits_rel', 'MuonHits_rel'],
    "KeepCollectionNames": [],
    "LCIOOutputFile": [ the_args.output ],
    "LCIOWriteMode": ["WRITE_NEW"]
}



Refit.Parameters["InputTrackCollectionName"] = [ TRK_FILTER ]

# FilterTracks for jets

FilterTrk_jets = MarlinProcessorWrapper("FilterTrk")
FilterTrk_jets.OutputLevel = INFO
FilterTrk_jets.ProcessorType = "FilterTracks"
FilterTrk_jets.Parameters = {
    "BarrelOnly": ["False"], # If true, just keep tracks with only barrel hits
    "Chi2Spatial":  ["0.1"], # Spatial chi squared
    "InputTrackCollectionName": [ TRK_ACTS ],
    "MinPt": ["0.5"], # Minimum transverse momentum
    "NHitsInner": ["-1"], # Minimum number of hits on inner tracker
    "NHitsOuter": ["-1"], # Minimum number of hits on outer tracker
    "NHitsVertex": ["0"], # Minimum number of hits on vertex detector
    "NHitsTotal": ["3"], # Minimum number of hits on track
    "MaxHoles": ["5"], # maximum number of holes
    "MaxOutliers": ["20"], 
    "MinNdf": ["17"], # minimum value for ndf
    "OutputTrackCollectionName": [ TRK_FILTER ],
    "NNmethod": [""],
}

#Calorimeter digitization optimized for jets

DDCaloDigi_jets = MarlinProcessorWrapper("DDCaloDigiHard")
DDCaloDigi_jets.OutputLevel = INFO
DDCaloDigi_jets.ProcessorType = "DDCaloDigi_BIB"
DDCaloDigi_jets.Parameters = {
                           "CalibECALMIP": ["33.6"],
                           "CalibHCALMIP": ["0.0001"],
                           "CalibrECAL": ["1.3", "1.3"],
                           "CalibrHCALBarrel": ["49.2031079063"],
                           "CalibrHCALEndcap": ["53.6263377733"],
                           "CalibrHCALOther": ["62.2125698179"],
                           "CrilinBarrelThreshold": ["2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2."],
                           "CrilinBarrelTimeMax": ["2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2."],
                           "CrilinBarrelTimeMin": ["-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1."],
                           "CrilinEndcapThreshold": ["2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2."],
                           "CrilinEndcapTimeMax": ["2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2.", "2."],
                           "CrilinEndcapTimeMin": ["-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1.", "-1."],
                           "CrilinPreselectionTimeCut": ["0.5"],
                           "SignalDecayConstant": ["10."],
                           "SignalTriggerThresholdsBarrel": ["40.", "40.", "40.", "40.", "40.", "40."],
                           "SignalTriggerThresholdsEndcap" : ["40.", "40.", "40.", "40.", "40.", "40."],
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
                           "energyPerEHpair": ["1000"]
                           }

DDCaloDigi_jets.Parameters["CrilinBarrelThreshold"] = ["150.", "150.", "150.", "50.", "50.", "50.", "20.", "20.", "20.", "15.", "15.", "15.", "10.", "10.", "10.", "10.", "10.", "10."]
DDCaloDigi_jets.Parameters["CrilinEndcapThreshold"] = ["400.", "250.", "250.", "160.", "110.", "80.", "80.", "50.", "40.", "50.", "30.", "20.", "40.", "20.", "10.", "40.", "10.", "10."]
DDCaloDigi_jets.Parameters["CrilinBarrelTimeMin"] = ["-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1"]
DDCaloDigi_jets.Parameters["CrilinEndcapTimeMin"] = ["-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1", "-0.1" ]
DDCaloDigi_jets.Parameters["CrilinBarrelTimeMax"] = ["0.2", "0.12",  "0.1",  "0.2", "0.12", "0.1", "0.2", "0.15", "0.15",  "0.2", "0.15", "0.15", "0.25", "0.2", "0.2", "0.3", "0.25", "0.3"]
DDCaloDigi_jets.Parameters["CrilinEndcapTimeMax"] = ["0.2", "0.1", "0.3",  "0.3", "0.3", "0.3",  "0.3", "0.3", "0.3", "0.3", "0.3", "0.3",  "0.2",  "0.3", "0.3", "0.2", "0.3", "0.3"]
DDCaloDigi_jets.Parameters["SignalTriggerThresholdsBarrel"] = ["150.", "50.", "20.", "15.", "10.", "10."]
DDCaloDigi_jets.Parameters["SignalTriggerThresholdsEndcap"] = ["250.", "80.", "40.", "20.", "10.", "10."]

#DDMarlinPandora conf optimized for jets

DDMarlinPandora_jets = MarlinProcessorWrapper("DDMarlinPandora")
DDMarlinPandora_jets.OutputLevel = INFO
DDMarlinPandora_jets.ProcessorType = "DDPandoraPFANewProcessor"
DDMarlinPandora_jets.Parameters = {
    "ClusterCollectionName": [ CLUSTER ],
    "CreateGaps": ["false"],
    "CurvatureToMomentumFactor": ["0.00015"],
    "D0TrackCut": ["5000"],
    "D0UnmatchedVertexTrackCut": ["5000"],
    "DigitalMuonHits": ["0"],
    "ECalBarrelNormalVector": ["0", "0", "1"],
    "ECalCaloHitCollections": [ECB_d, ECE_d],
    "ECalMipThreshold": ["0.5"],
    "ECalScMipThreshold": ["0"],
    "ECalScToEMGeVCalibration": ["1"],
    "ECalScToHadGeVCalibrationBarrel": ["1"],
    "ECalScToHadGeVCalibrationEndCap": ["1"],
    "ECalScToMipCalibration": ["1"],
    "ECalSiMipThreshold": ["0"],
    "ECalSiToEMGeVCalibration": ["1"],
    "ECalSiToHadGeVCalibrationBarrel": ["1"],
    "ECalSiToHadGeVCalibrationEndCap": ["1"],
    "ECalSiToMipCalibration": ["1"],
    "ECalToEMGeVCalibration": ["1"],
    "ECalToHadGeVCalibrationBarrel": ["1"],
    "ECalToHadGeVCalibrationEndCap": ["1"],
    "ECalToMipCalibration": ["181.818"],
    "EMConstantTerm": ["0.01"],
    "EMStochasticTerm": ["0.15"],
    "FinalEnergyDensityBin": ["110."],
    "HCalBarrelNormalVector": ["0", "0", "1"],
    "HCalCaloHitCollections": [HCB_d, HCE_d],
    "HCalMipThreshold": ["0.3"],
    "HCalToEMGeVCalibration": ["1.02373335516"],
    "HCalToHadGeVCalibration": ["1.01799349172"],
    "HCalToMipCalibration": ["40.8163"],
    "HadConstantTerm": ["0.03"],
    "HadStochasticTerm": ["0.6"],
    "InputEnergyCorrectionPoints": [],
    "KinkVertexCollections": ["KinkVertices"],
    "LayersFromEdgeMaxRearDistance": ["250"],
    "MCParticleCollections": [ MCP ],
    "MaxBarrelTrackerInnerRDistance": ["200"],
    "MaxClusterEnergyToApplySoftComp": ["2000."],
    "MaxHCalHitHadronicEnergy": ["1000000"],
    "MaxTrackHits": ["5000"],
    "MaxTrackSigmaPOverP": ["5000"],
    "MinBarrelTrackerHitFractionOfExpected": ["0"],
    "MinCleanCorrectedHitEnergy": ["0.1"],
    "MinCleanHitEnergy": ["0.5"],
    "MinCleanHitEnergyFraction": ["0.01"],
    "MinFtdHitsForBarrelTrackerHitFraction": ["0"],
    "MinFtdTrackHits": ["0"],
    "MinMomentumForTrackHitChecks": ["0"],
    "MinTpcHitFractionOfExpected": ["0"],
    "MinTrackECalDistanceFromIp": ["0"],
    "MinTrackHits": ["0"],
    "MuonBarrelBField": ["-1.34"],
    "MuonCaloHitCollections": [MuD_d],
    "MuonEndCapBField": ["0.01"],
    "MuonHitEnergy": ["0.5"],
    "MuonToMipCalibration": ["19607.8"],
    "NEventsToSkip": ["0"],
    "NOuterSamplingLayers": ["3"],
    "OutputEnergyCorrectionPoints": [],
    "PFOCollectionName": [ PFO ],
    "PandoraSettingsXmlFile": [ "conf/PandoraSettings/PandoraSettingsJets.xml" ],
    "ProngVertexCollections": ["ProngVertices"],
    "ReachesECalBarrelTrackerOuterDistance": ["-100"],
    "ReachesECalBarrelTrackerZMaxDistance": ["-50"],
    "ReachesECalFtdZMaxDistance": ["1"],
    "ReachesECalMinFtdLayer": ["0"],
    "ReachesECalNBarrelTrackerHits": ["0"],
    "ReachesECalNFtdHits": ["0"],
    "RelCaloHitCollections": [CALO_r, MUON_r],
    "RelTrackCollections": [ TRK_REFIT_r ],
    "ShouldFormTrackRelationships": ["1"],
    "ShouldUseTrackSeed": ["false"],
    "SoftwareCompensationEnergyDensityBins": ["0", "2.", "5.", "7.5", "9.5", "13.", "16.", "20.", "23.5", "28.", "33.", "40.", "50.", "75.", "100."],
    "SoftwareCompensationWeights": ["1.61741", "-0.00444385", "2.29683e-05", "-0.0731236", "-0.00157099", "-7.09546e-07", "0.868443", "1.0561", "-0.0238574"],
    "SplitVertexCollections": ["SplitVertices"],
    "StartVertexAlgorithmName": ["PandoraPFANew"],
    "StartVertexCollectionName": [ VTX_start ],
    "StripSplittingOn": ["0"],
    "TrackCollections": [ TRK_REFIT ],
    "TrackCreatorName": ["DDTrackCreatorCLIC"],
    "TrackStateTolerance": ["0"],
    "TrackSystemName": ["DDKalTest"],
    "UnmatchedVertexTrackMaxEnergy": ["5000"],
    "UseEcalScLayers": ["0"],
    "UseNonVertexTracks": ["1"],
    "UseOldTrackStateCalculation": ["0"],
    "UseUnmatchedNonVertexTracks": ["1"],
    "UseUnmatchedVertexTracks": ["1"],
    "V0VertexCollections": ["V0Vertices"],
    "YokeBarrelNormalVector": ["0", "0", "1"],
    "Z0TrackCut": ["10000"],
    "Z0UnmatchedVertexTrackCut": ["5000"],
    "ZCutForNonVertexTracks": ["10000"],
    "CrilinBarrelOffsets": ["442.9","367.7","220.0",  "96.99","76.38","37.8",  "26.43","19.0","8.787",  "8.255","6.482","4.93",  "0.","0.","0.",  "0.","0.","0."],
    "CrilinEndcapOffsets": ["296.4","221.6","150.4",  "95.44","57.78","37.8",  "33.38","17.05","9.763",  "0.","0.","0.",  "0.","0.","0.",  "0.","0.","0."]
}


#PandoraPFO selector optimized for jets
#At least for now it is basically a pass through

PFOSelection_jets = MarlinProcessorWrapper("PFOSelection")
PFOSelection_jets.OutputLevel = INFO
PFOSelection_jets.ProcessorType = "CLICPfoSelector"
PFOSelection_jets.Parameters = {
    "ChargedPfoLooseTimingCut": ["1000"],
    "ChargedPfoNegativeLooseTimingCut": ["-1000"],
    "ChargedPfoNegativeTightTimingCut": ["-1000"],
    "ChargedPfoPtCut": ["0"],
    "ChargedPfoPtCutForLooseTiming": ["0"],
    "ChargedPfoTightTimingCut": ["1000"],
    "CheckKaonCorrection": ["0"],
    "CheckProtonCorrection": ["0"],
    "ClusterLessPfoTrackTimeCut": ["1000"],
    "CorrectHitTimesForTimeOfFlight": ["0"],
    "DisplayRejectedPfos": ["1"],
    "DisplaySelectedPfos": ["1"],
    "FarForwardCosTheta": ["0.975"],
    "ForwardCosThetaForHighEnergyNeutralHadrons": ["0.95"],
    "ForwardHighEnergyNeutralHadronsEnergy": ["1000"],
    "HCalBarrelLooseTimingCut": ["2000"],
    "HCalBarrelTightTimingCut": ["1000"],
    "HCalEndCapTimingFactor": ["1"],
    "InputPfoCollection": [ PFO ],
    "KeepKShorts": ["1"],
    "MaxMomentumForClusterLessPfos": ["1000"],
    "MinECalHitsForTiming": ["0"],
    "MinHCalEndCapHitsForTiming": ["0"],
    "MinMomentumForClusterLessPfos": ["0"],
    "MinPtForClusterLessPfos": ["0"],
    "MinimumEnergyForNeutronTiming": ["0"],
    "Monitoring": ["0"],
    "MonitoringPfoEnergyToDisplay": ["1"],
    "NeutralFarForwardLooseTimingCut": ["1000"],
    "NeutralFarForwardTightTimingCut": ["1000"],
    "NeutralHadronBarrelPtCutForLooseTiming": ["1000"],
    "NeutralHadronLooseTimingCut": ["1000"],
    "NeutralHadronPtCut": ["0"],
    "NeutralHadronPtCutForLooseTiming": ["0"],
    "NeutralHadronTightTimingCut": ["1000"],
    "PhotonFarForwardLooseTimingCut": ["1000"],
    "PhotonFarForwardTightTimingCut": ["1000"],
    "PhotonLooseTimingCut": ["1000"],
    "PhotonPtCut": ["0"],
    "PhotonPtCutForLooseTiming": ["0"],
    "PhotonTightTimingCut": ["1000"],
    "PtCutForTightTiming": ["0"],
    "SelectedPfoCollection": [ PFO_sel ],
    "UseClusterLessPfos": ["1"],
    "UseNeutronTiming": ["0"]
}

MyTrueMCintoRecoForJets = MarlinProcessorWrapper("MyTrueMCintoRecoForJets")
MyTrueMCintoRecoForJets.OutputLevel = INFO
MyTrueMCintoRecoForJets.ProcessorType = "TrueMCintoRecoForJets"
MyTrueMCintoRecoForJets.Parameters = {
                                      "MCParticleInputCollectionName": ["MCPhysicsParticle"],
                                      "RECOParticleCollectionName": ["MCParticlePandoraPFOs"],
                                      "RecoParticleInputCollectionName": ["PandoraPFOs"],
                                      "RecoParticleNoLeptonCollectionName": ["PandoraPFOsNoLeptons"],
                                      "cosAngle_pfo_lepton": ["0.995"],
                                      "ignoreNeutrinosInMCJets": ["true"],
                                      "vetoBosonLeptons": ["false"],
                                      "vetoBosonLeptonsOnReco": ["false"]
                                      }

MyFastGenJetProcessor = MarlinProcessorWrapper("MyFastGenJetProcessor")
MyFastGenJetProcessor.OutputLevel = INFO
MyFastGenJetProcessor.ProcessorType = "FastJetProcessor"
MyFastGenJetProcessor.Parameters = {
                                    "algorithm": ["kt_algorithm", "0.5"],
                                    "clusteringMode": ["Inclusive", "5"],
                                    "jetOut": ["GenJet_VLC"],
                                    "recParticleIn": ["MCParticlePandoraPFOs"],
                                    "recParticleOut": ["MCParticlePandoraPFOsInJet"],
                                    "recombinationScheme": ["E_scheme"],
                                    "storeParticlesInJets": ["true"]
                                    }


MyJetAnalyzer = MarlinProcessorWrapper("MyJetAnalyzer")
MyJetAnalyzer.OutputLevel = INFO
MyJetAnalyzer.ProcessorType = "JetAnalyzer"
MyJetAnalyzer.Parameters = {
                            "GenJetCollection": ["GenJet_VLC"],
                            "MCParticleCollectionName": ["MCParticle"],
                            "OutputRootFileName": ["tuples.root"],
                            "RECOParticleCollectionName": ["PandoraPFOs"],
                            "ProcessName": ["dijet"],
                            #"RecoJetCollection": ["JetOut_kt"],
                            "RecoJetCollection": ["BuildUpVertices_RP"],
                            "doDiBosonChecks": ["false"],
                            "fillMEInfo": ["true"]
                            }



### Modify timing threshold (by Massimo C.)
DDSimpleMuonDigi.Parameters["CalibrMUON"] = ["1."]
DDSimpleMuonDigi.Parameters["MuonTimeThreshold"] = ["1e-07"]                                 
DDSimpleMuonDigi.Parameters["MuonThreshold"] = ["1e-07"]   

#### Execution list

algList.append(AIDA)
algList.append(EventNumber)
algList.append(Config)
algList.append(DD4hep)

# Overlay
if the_args.overlay == "full":
    algList.append(OverlayBIB)  # Config.OverlayBIB
elif the_args.overlay == "trimmed":
    algList.append(OverlayTrimmed)  # Config.OverlayTrimmed
elif the_args.overlay == "none":
    algList.append(OverlayFalse)  # Config.OverlayFalse
elif the_args.overlay == "test":
    algList.append(OverlayTest)  # Config.OverlayTest

# Digitization
algList.append(VXDBarrelDigitiser)
algList.append(VXDEndcapDigitiser)
algList.append(InnerPlanarDigiProcessor)
algList.append(InnerEndcapPlanarDigiProcessor)
algList.append(OuterPlanarDigiProcessor)
algList.append(OuterEndcapPlanarDigiProcessor)
algList.append(DDCaloDigi_jets)
algList.append(DDSimpleMuonDigi)

# Tracking
algList.append(CKFTrackingNoIl)
algList.append(TrackDeduplication)
algList.append(FilterTrk_jets)
algList.append(Refit)

# Calo
algList.append(DDMarlinPandora_jets)
algList.append(PFOSelection_jets)

# Jet
algList.append(FastJetProcessor_kt)

# Cone tracking
algList.append(FilterHitsJets)
algList.append(CKFTrackingFilteredHits)
algList.append(TrackDeduplicationCone)
algList.append(FilterTracksCone)
algList.append(TrackDeduplicationSecond)

# Vertex finder
algList.append(TrkToPFOConverter)
algList.append(VertexFinder)

# root tuple
algList.append(MyTrueMCintoRecoForJets)
algList.append(MyFastGenJetProcessor)
algList.append(MyJetAnalyzer)
algList.append(JET_kt_LCTuple)
algList.append(TrueJets)

# Output
#algList.append(LCIOWriter_all)
algList.append(LCIOWriter_light)

from Configurables import ApplicationMgr
ApplicationMgr( TopAlg = algList,
                EvtSel = 'NONE',
                EvtMax   = the_args.nevt,
                ExtSvc = [evtsvc],
                OutputLevel = DEBUG
              )


