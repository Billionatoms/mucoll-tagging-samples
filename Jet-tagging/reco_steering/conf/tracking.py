from Gaudi.Configuration import *
from Configurables import MarlinProcessorWrapper

from constants import *

######################################
#### Defines the following processors:
# CKFTracking
# CKFTrackingNoIl # remove first layer of Vertex Det.
# TrackDeduplication
# FilterTracks
# Refit
# TrackTruth
# TrackPerf
# MergeSim
# MergeHits
######################################

# Default values
import os
DETSCHEMA    = "MuSIC_v2"
ACTSDATA     = os.environ.get("ACTS_DATA", "/usr/share/ACTSTracking/data/")
MATFILE      = ACTSDATA + "material-maps.json"
TGEOFILE     = ACTSDATA + "MuSIC_v2.root"
TGEODESCFILE = ACTSDATA + "MuSIC_v2.json"

CKFTracking = MarlinProcessorWrapper("CKFTracking")
CKFTracking.OutputLevel = INFO
CKFTracking.ProcessorType = "ACTSSeededCKFTrackingProc"
CKFTracking.Parameters = {
    "DetectorSchema": [ DETSCHEMA ],
    "CKF_Chi2CutOff": ["10"],
    "CKF_NumMeasurementsCutOff": ["1"],
    "MatFile": [ MATFILE ],
    "PropagateBackward": ["False"],
    "RunCKF": ["True"],
    "SeedFinding_CollisionRegion": ["3.5"],
    "SeedFinding_DeltaRMax": ["80"],
    "SeedFinding_DeltaRMin": ["2"],
    "SeedFinding_DeltaRMaxBottom": ["80"],
    "SeedFinding_DeltaRMaxTop": ["80"],
    "SeedFinding_DeltaRMinBottom": ["5"],
    "SeedFinding_DeltaRMinTop": ["2"],
    "SeedFinding_ImpactMax": ["3"],
    "SeedFinding_MinPt": ["500"],
    "SeedFinding_RMax": ["150"],
    "SeedFinding_ZMax": ["500"],
    "SeedFinding_RadLengthPerSeed": ["0.1"],
    "SeedFinding_zBottomBinLen": ["1"],
    "SeedFinding_zTopBinLen": ["1"],
    "SeedFinding_phiBottomBinLen": ["1"],
    "SeedFinding_phiTopBinLen": ["1"],
    "SeedFinding_SigmaScattering": ["3"],
    "SeedingLayers": [
         "13", "8", "13", "6", "13", "4", "13", "2",
         "14", "2", "14", "4", "14", "6", "14", "8",
         "15", "2", "15", "4", "15", "6", "15", "8",
         ],
    "TGeoFile": [ TGEOFILE ],
    "TGeoDescFile": [ TGEODESCFILE ],
    "TrackCollectionName": [ TRK_RAW ],
    "TrackerHitCollectionNames": [ VXDB_d, VXDE_d, ITDB_d, ITDE_d, OTDB_d, OTDE_d ],
    "CaloFace_Radius": ["1500"],
    "CaloFace_Z": ["2307"]
}

CKFTrackingNoIl = MarlinProcessorWrapper("CKFTrackingNoIl")
CKFTrackingNoIl.OutputLevel = INFO
CKFTrackingNoIl.ProcessorType = "ACTSSeededCKFTrackingProc"
CKFTrackingNoIl.Parameters = {
    "DetectorSchema": [ DETSCHEMA ],
    "CKF_Chi2CutOff": ["10"],
    "CKF_NumMeasurementsCutOff": ["1"],
    "MatFile": [ MATFILE ],
    "PropagateBackward": ["False"],
    "RunCKF": ["True"],
    "SeedFinding_CollisionRegion": ["3.5"],
    "SeedFinding_DeltaRMax": ["80"],
    "SeedFinding_DeltaRMin": ["2"],
    "SeedFinding_DeltaRMaxBottom": ["80"],
    "SeedFinding_DeltaRMaxTop": ["80"],
    "SeedFinding_DeltaRMinBottom": ["5"],
    "SeedFinding_DeltaRMinTop": ["2"],
    "SeedFinding_ImpactMax": ["3"],
    "SeedFinding_MinPt": ["500"],
    "SeedFinding_RMax": ["150"],
    "SeedFinding_ZMax": ["500"],
    "SeedFinding_RadLengthPerSeed": ["0.1"],
    "SeedFinding_zBinEdges": ["-130", "-65", "0", "65", "130"],
    "SeedFinding_zBottomBinLen": ["1"],
    "SeedFinding_zTopBinLen": ["1"],
    "SeedFinding_phiBottomBinLen": ["1"],
    "SeedFinding_phiTopBinLen": ["1"],
    "SeedFinding_SigmaScattering": ["3"],
    "SeedingLayers": [
         "13", "8", "13", "6", "13", "4", "13", "2",
         "14", "4", "14", "6", "14", "8", "14", "10",
         "15", "2", "15", "4", "15", "6", "15", "8",
         ],
    "TGeoFile": [ TGEOFILE ],
    "TGeoDescFile": [ TGEODESCFILE ],
    "TrackCollectionName": [ TRK_RAW ],
    "TrackerHitCollectionNames": [ VXDB_d, VXDE_d, ITDB_d, ITDE_d, OTDB_d, OTDE_d ],
    "CaloFace_Radius": ["1500"],
    "CaloFace_Z": ["2307"]
}

#### Tracking with filtered hits
CKFTrackingFilteredHits = MarlinProcessorWrapper("CKFTrackingFilteredHits")
CKFTrackingFilteredHits.OutputLevel = INFO
CKFTrackingFilteredHits.ProcessorType = "ACTSSeededCKFTrackingProc"
CKFTrackingFilteredHits.Parameters = {
    "DetectorSchema": [ DETSCHEMA ],
    "CKF_Chi2CutOff": ["10"],
    "CKF_NumMeasurementsCutOff": ["1"],
    "MatFile": [ MATFILE ],
    "PropagateBackward": ["False"],
    "RunCKF": ["True"],
    "SeedFinding_CollisionRegion": ["3.5"],
    "SeedFinding_DeltaRMax": ["80"],
    "SeedFinding_DeltaRMin": ["2"],
    "SeedFinding_DeltaRMaxBottom": ["80"],
    "SeedFinding_DeltaRMaxTop": ["80"],
    "SeedFinding_DeltaRMinBottom": ["5"],
    "SeedFinding_DeltaRMinTop": ["2"],
    "SeedFinding_ImpactMax": ["3"],
    "SeedFinding_MinPt": ["500"],
    "SeedFinding_RMax": ["150"],
    "SeedFinding_ZMax": ["500"],
    "SeedFinding_RadLengthPerSeed": ["0.1"],
    "SeedFinding_zBottomBinLen": ["1"],
    "SeedFinding_zTopBinLen": ["1"],
    "SeedFinding_phiBottomBinLen": ["1"],
    "SeedFinding_phiTopBinLen": ["1"],
    "SeedFinding_SigmaScattering": ["3"],
    "SeedingLayers": [
         "13", "8", "13", "6", "13", "4", "13", "2",
         "14", "2", "14", "4", "14", "6", "14", "8",
         "15", "2", "15", "4", "15", "6", "15", "8",
         ],
    "TGeoFile": [ TGEOFILE ],
    "TGeoDescFile": [ TGEODESCFILE ],
    "TrackCollectionName": [ TRK_RAW_c ],
    "TrackerHitCollectionNames": [ VXDB_c, VXDE_c, ITDB_c, ITDE_c, OTDB_c, OTDE_c ],
    "SeedCollectionName": ["SeedTracks_cone"],
    "CaloFace_Radius": ["1500"],
    "CaloFace_Z": ["2307"]
}


CKFTruth = MarlinProcessorWrapper("CKFTruth")
CKFTruth.OutputLevel = INFO
CKFTruth.ProcessorType = "ACTSTruthCKFTrackingProc"
CKFTruth.Parameters = {
    "DetectorSchema": [ DETSCHEMA ],
    "CKF_Chi2CutOff": ["10"],
    "CKF_NumMeasurementsCutOff": ["1"],
    "MatFile": [ MATFILE ],
    "TGeoFile": [ TGEOFILE ],
    "TGeoDescFile": [ TGEODESCFILE ],
    "TrackCollectionName": [ TRK_TRUTH ],
    "TrackerHitCollectionNames": [ VXDB_d, VXDE_d, ITDB_d, ITDE_d, OTDB_d, OTDE_d ],
    "CaloFace_Radius": ["1500"],
    "CaloFace_Z": ["2307"]
}


TrackDeduplication = MarlinProcessorWrapper("TrackDeduplication")
TrackDeduplication.OutputLevel = INFO
TrackDeduplication.ProcessorType = "ACTSDuplicateRemoval"
TrackDeduplication.Parameters = {
    "InputTrackCollectionName": [ TRK_RAW ],
    "OutputTrackCollectionName": [ TRK_ACTS ]
}



TrackDeduplicationCone = MarlinProcessorWrapper("TrackDeduplicationCone")
TrackDeduplicationCone.OutputLevel = INFO
TrackDeduplicationCone.ProcessorType = "ACTSDuplicateRemoval"
TrackDeduplicationCone.Parameters = {
    "InputTrackCollectionName": [ TRK_RAW_c ],
    "OutputTrackCollectionName": [ TRK_ACTS_c ]
}

TrackDeduplicationSecond = MarlinProcessorWrapper("TrackDeduplicationSecond")
TrackDeduplicationSecond.OutputLevel = INFO
TrackDeduplicationSecond.ProcessorType = "ACTSDuplicateRemoval"
TrackDeduplicationSecond.Parameters = {
    "InputTrackCollectionName": [ TRK_FILTER_c ],
    "OutputTrackCollectionName": [ "Tracks_deduplized" ]
}






# FilterTracks processor filters a collection of tracks based on NHits and MinPt and outputs a filtered collection
FilterTracks = MarlinProcessorWrapper("FilterTracks")
FilterTracks.OutputLevel = INFO
FilterTracks.ProcessorType = "FilterTracks"
FilterTracks.Parameters = {
    "BarrelOnly": ["False"], # If true, just keep tracks with only barrel hits
    "Chi2Spatial":  ["0.1"], # Spatial chi squared
    "InputTrackCollectionName": [ TRK_ACTS ],
    "MinPt": ["0.5"], # Minimum transverse momentum in GeV
    "MaxPt": ["1000"], # Max transverse momentum in GeV
    "NHitsInner": ["-1"], # Minimum number of hits on inner tracker
    "NHitsOuter": ["-1"], # Minimum number of hits on outer tracker
    "NHitsVertex": ["0"], # Minimum number of hits on vertex detector
    "NHitsTotal": ["3"], # Minimum number of hits on track
    "MaxHoles": ["5"], # maximum number of holes 
    "MinNdf": ["12"], # minimum value for ndf
    "OutputTrackCollectionName": [ TRK_FILTER ],
    "NNmethod": [""],
    #"NNmethod": ["BDT::BDTG"],
    "NNweights": ["TMVAClassification_BDTG.weights.xml"],
    # supported variables are: trtvhn, trtihn, trtohn, trthn, trtnh, trch2, trndf    
    "NNvars": ["trtihn", "trtohn", "trtvhn", "trch2", "trndf"],
    "NNthr": ["0.09"]            
}

# FilterTracks processor filters a collection of tracks based on NHits and MinPt and outputs a filtered collection
FilterTracksCone = MarlinProcessorWrapper("FilterTracksCone")
FilterTracksCone.OutputLevel = INFO
FilterTracksCone.ProcessorType = "FilterTracks"
FilterTracksCone.Parameters = {
    "BarrelOnly": ["False"], # If true, just keep tracks with only barrel hits
    "Chi2Spatial":  ["0.1"], # Spatial chi squared
    "InputTrackCollectionName": [ TRK_ACTS_c ],
    "MinPt": ["0.5"], # Minimum transverse momentum
    "NHitsInner": ["-1"], # Minimum number of hits on inner tracker
    "NHitsOuter": ["-1"], # Minimum number of hits on outer tracker
    "NHitsVertex": ["2"], # Minimum number of hits on vertex detector   !!(AT LEAST 3 HITS IN VXD, OTHERWISE NO RELIABLE D0-Z0)!!
    "NHitsTotal": ["3"], # Minimum number of hits on track
    "MaxHoles": ["5"], # maximum number of holes
    "MinNdf": ["13"], # minimum value for ndf
    "MaxOutliers": ["5"], # max number of hits removed in the fit
    "MaxOutliersOverHits": ["0.1"], # max ratio of (hits removed in the fit)/(total hits)
    "MaxSigmaD0": ["0.03"],     # max error on track D0
    "MaxSigmaZ0": ["0.001"],     # max error on track Z0
    "MaxSigmaTheta": ["0.15"],  # max error on track Theta
    "MaxSigmaPhi": ["0.000004"],    # max error on track Phi
    "MaxSigmaQoverP": ["0.1"], # max error on track q/p
    "OutputTrackCollectionName": [ TRK_FILTER_c ],
    "NNmethod": [""],
    #"NNmethod": ["BDT::BDTG"],
    "NNweights": ["/users/muoncollider/zuliani/EUstrat/mucoll-benchmarks/analysis/physics_performance/dataset/H_weights/TMVAClassification_BDTG.weights.xml"],
    # supported variables are: trtvhn, trtihn, trtohn, trthn, trtnh, trch2, trndf
    "NNvars": ["trtihn", "trtohn", "trtvhn", "trch2", "trndf"],
    "NNthr": ["0.09"]
}




Refit = MarlinProcessorWrapper("Refit")
Refit.OutputLevel = WARNING
Refit.ProcessorType = "RefitFinal"
Refit.Parameters = {
    "EnergyLossOn": ["true"],
    "InputRelationCollectionName": [ TRK_MC_r ],
    "InputTrackCollectionName": [ TRK_ACTS ],
    "Max_Chi2_Incr": ["1.79769e+30"],
    "MinClustersOnTrackAfterFit": ["3"],
    "MultipleScatteringOn": ["true"],
    "OutputRelationCollectionName": [ TRK_REFIT_r ],
    "OutputTrackCollectionName": [ TRK_REFIT ],
    "ReferencePoint": ["-1"],
    "SmoothOn": ["false"],
    "extrapolateForward": ["true"]
}

TrackTruth = MarlinProcessorWrapper("TrackTruth")
TrackTruth.OutputLevel = INFO
TrackTruth.ProcessorType = "TrackTruthProc"
TrackTruth.Parameters = {
    "TrackCollection": [ TRK_ACTS ],
    "MCParticleCollection": [ MCP ],
    "TrackerHit2SimTrackerHitRelationName": [ VXDB_r, VXDE_r, ITDB_r, ITDE_r, OTDB_r, OTDE_r ],
    "Particle2TrackRelationName": [ TRK_MC_r ],
}

TrackPerf = MarlinProcessorWrapper("TrackPerf")
TrackPerf.OutputLevel = INFO
TrackPerf.ProcessorType = "TrackPerfHistProc"
TrackPerf.Parameters = {
    "MCParticleCollection": [ MCP ],
    "MCTrackRelationCollection": [ TRK_MC_r ],
    "MatchProb": ['0.5'],
    "TrackCollection": [ TRK_ACTS ],
}

MergeSim = MarlinProcessorWrapper("MergeSim")
MergeSim.OutputLevel = INFO
MergeSim.ProcessorType = "MergeCollections"
MergeSim.Parameters = {
    "InputCollections": [ VXDB_s, VXDE_s, ITDB_s, ITDE_s, OTDB_s, OTDE_s ],
    "OutputCollection": [ ALL_sim ],
}

MergeHits = MarlinProcessorWrapper("MergeHits")
MergeHits.OutputLevel = INFO
MergeHits.ProcessorType = "MergeCollections"
MergeHits.Parameters = {
    "InputCollections": [ VXDB_d, VXDE_d, ITDB_d, ITDE_d, OTDB_d, OTDE_d ],
    "OutputCollection": [ ALL_digit ],
}


