from Gaudi.Configuration import *
from Configurables import MarlinProcessorWrapper

from constants import *

######################################
#### Defines the following processor:
# 
######################################

# Default values
PANDORA_SETTINGS = "/MuSIC10TeV/conf/PandoraSettings/PandoraSettingsDefault.xml"

#### Processors
DDMarlinPandora = MarlinProcessorWrapper("DDMarlinPandora")
DDMarlinPandora.OutputLevel = INFO
DDMarlinPandora.ProcessorType = "DDPandoraPFANewProcessor"
DDMarlinPandora.Parameters = {
    "ClusterCollectionName": [ CLUSTER ],
    "CreateGaps": ["false"],
    "CurvatureToMomentumFactor": ["0.00015"],
    "D0TrackCut": ["200"],
    "D0UnmatchedVertexTrackCut": ["5"],
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
    "ECalToEMGeVCalibration": ["1.02373335516"],
    "ECalToHadGeVCalibrationBarrel": ["1.24223718397"],
    "ECalToHadGeVCalibrationEndCap": ["1.24223718397"],
    "ECalToMipCalibration": ["181.818"],
    "EMConstantTerm": ["0.01"],
    "EMStochasticTerm": ["0.17"],
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
    "MaxTrackSigmaPOverP": ["0.15"],
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
    "PandoraSettingsXmlFile": [ PANDORA_SETTINGS ],
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
    "UnmatchedVertexTrackMaxEnergy": ["5"],
    "UseEcalScLayers": ["0"],
    "UseNonVertexTracks": ["1"],
    "UseOldTrackStateCalculation": ["0"],
    "UseUnmatchedNonVertexTracks": ["0"],
    "UseUnmatchedVertexTracks": ["1"],
    "V0VertexCollections": ["V0Vertices"],
    "YokeBarrelNormalVector": ["0", "0", "1"],
    "Z0TrackCut": ["200"],
    "Z0UnmatchedVertexTrackCut": ["5"],
    "ZCutForNonVertexTracks": ["250"]
}

PFOSelection = MarlinProcessorWrapper("PFOSelection")
PFOSelection.OutputLevel = INFO
PFOSelection.ProcessorType = "CLICPfoSelector"
PFOSelection.Parameters = {
    "ChargedPfoLooseTimingCut": ["3"],
    "ChargedPfoNegativeLooseTimingCut": ["-1"],
    "ChargedPfoNegativeTightTimingCut": ["-0.5"],
    "ChargedPfoPtCut": ["0"],
    "ChargedPfoPtCutForLooseTiming": ["4"],
    "ChargedPfoTightTimingCut": ["1.5"],
    "CheckKaonCorrection": ["0"],
    "CheckProtonCorrection": ["0"],
    "ClusterLessPfoTrackTimeCut": ["10"],
    "CorrectHitTimesForTimeOfFlight": ["0"],
    "DisplayRejectedPfos": ["1"],
    "DisplaySelectedPfos": ["1"],
    "FarForwardCosTheta": ["0.975"],
    "ForwardCosThetaForHighEnergyNeutralHadrons": ["0.95"],
    "ForwardHighEnergyNeutralHadronsEnergy": ["10"],
    "HCalBarrelLooseTimingCut": ["20"],
    "HCalBarrelTightTimingCut": ["10"],
    "HCalEndCapTimingFactor": ["1"],
    "InputPfoCollection": [ PFO ],
    "KeepKShorts": ["1"],
    "MaxMomentumForClusterLessPfos": ["2"],
    "MinECalHitsForTiming": ["5"],
    "MinHCalEndCapHitsForTiming": ["5"],
    "MinMomentumForClusterLessPfos": ["0.5"],
    "MinPtForClusterLessPfos": ["0.5"],
    "MinimumEnergyForNeutronTiming": ["1"],
    "Monitoring": ["0"],
    "MonitoringPfoEnergyToDisplay": ["1"],
    "NeutralFarForwardLooseTimingCut": ["2"],
    "NeutralFarForwardTightTimingCut": ["1"],
    "NeutralHadronBarrelPtCutForLooseTiming": ["3.5"],
    "NeutralHadronLooseTimingCut": ["2.5"],
    "NeutralHadronPtCut": ["0"],
    "NeutralHadronPtCutForLooseTiming": ["8"],
    "NeutralHadronTightTimingCut": ["1.5"],
    "PhotonFarForwardLooseTimingCut": ["2"],
    "PhotonFarForwardTightTimingCut": ["1"],
    "PhotonLooseTimingCut": ["2"],
    "PhotonPtCut": ["0"],
    "PhotonPtCutForLooseTiming": ["4"],
    "PhotonTightTimingCut": ["1"],
    "PtCutForTightTiming": ["0.75"],
    "SelectedPfoCollection": [ PFO_sel ],
    "UseClusterLessPfos": ["1"],
    "UseNeutronTiming": ["0"]
}

FastJetProcessor = MarlinProcessorWrapper("FastJetProcessor")
FastJetProcessor.OutputLevel = INFO
FastJetProcessor.ProcessorType = "FastJetProcessor"
FastJetProcessor.Parameters = {
    "algorithm": ["antikt_algorithm", "0.5"],
    "clusteringMode": ["Inclusive", "5"],
    "jetOut": [ JET ],
    "recParticleIn": [ PFO_sel ],
    "recombinationScheme": ["E_scheme"]
}


FastJetProcessor_antikt = MarlinProcessorWrapper("FastJetProcessor_antikt")
FastJetProcessor_antikt.OutputLevel = DEBUG
FastJetProcessor_antikt.ProcessorType = "FastJetProcessor"
FastJetProcessor_antikt.Parameters = {
    "algorithm": ["antikt_algorithm", "0.5"],
    "clusteringMode": ["Inclusive", "5"],
    "jetOut": ["JetOut_antikt"],
    "recParticleIn": [ PFO_sel ],
    "recombinationScheme": ["E_scheme"],
}


FastJetProcessor_kt = MarlinProcessorWrapper("FastJetProcessor_kt")
FastJetProcessor_kt.OutputLevel = DEBUG
FastJetProcessor_kt.ProcessorType = "FastJetProcessor"
FastJetProcessor_kt.Parameters = {
    "algorithm": ["kt_algorithm", "0.5"],
    "clusteringMode": ["Inclusive", "5"],
    "jetOut": ["JetOut_kt"],
    "recParticleIn": [ PFO_sel ],
    "recombinationScheme": ["E_scheme"],
}


