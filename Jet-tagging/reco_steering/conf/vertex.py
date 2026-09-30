from Gaudi.Configuration import *
from Configurables import MarlinProcessorWrapper

from constants import *


#Trk hits filtering with jets
FilterHitsJets = MarlinProcessorWrapper("FilterHitsJets")
FilterHitsJets.OutputLevel = DEBUG
FilterHitsJets.ProcessorType = "FilterJetConeHits"
FilterHitsJets.Parameters = {
    "JetCaloCollection": ["JetOut_kt"],
    "TrackerHitInputCollections": [ VXDB_d, VXDE_d, ITDB_d, ITDE_d, OTDB_d, OTDE_d ],
    "TrackerSimHitInputCollections": [ ],
    "TrackerHitInputRelations": [ ],
    "TrackerHitOutputCollections": [ VXDB_c, VXDE_c, ITDB_c, ITDE_c, OTDB_c, OTDE_c ],
    "TrackerSimHitOutputCollections": [ ],
    "TrackerHitOutputRelations": [ ],
    "DeltaRCut": ["1.0"], #1.0 is standard
    "MinJetTracks": ["1"],
    "MinDaughterMaxPt": ["2."],
    "MakeFilteredJetsCollection": ["true"],
    "FilteredJetsCollectionName": ["FakeRemovedJets"],
    "MakeDirectionCorrection": ["true"],    #direction correction in [30°,60°] see L. Sestini jet reconstruction
    "CorrectionConstant": ["338.177"],
    "CorrectionLinear": ["-23.4431"],
    "CorrectionQuadratic": ["0.568 "],
    "CorrectionCubic": ["-0.00423718"]
}

TrkToPFOConverter = MarlinProcessorWrapper("TrkToPFOConverter")
TrkToPFOConverter.OutputLevel = INFO
TrkToPFOConverter.ProcessorType = "TrackToPFOConverterProcessor"
TrkToPFOConverter.Parameters = {
    "InputTrackCollection": [ "Tracks_deduplized" ],
    "OutputPFOCollection": [ "PFOfromTracks_cone" ],
    "Bfield": ["5."]
}

# Vertex finder
VertexFinder = MarlinProcessorWrapper("VertexFinder")
VertexFinder.OutputLevel = DEBUG
VertexFinder.ProcessorType = "LcfiplusProcessor"
VertexFinder.Parameters = {
                           "Algorithms": ["PrimaryVertexFinder", "BuildUpVertex"],
                           "VerbosityDebug": ["true"],
                           "AllowToModifyEvent": ["true"],
                           "BeamSizeX": ["0.001"],
                           "BeamSizeY": ["0.001"],
                           "BeamSizeZ": ["1.5"],

                           "BuildUpVertex.OriginalJetCollectionName": ["FakeRemovedJets"],
                           "BuildUpVertex.JetSelectionCone": ["0.6"],

                           "BuildUpVertex.AVFTemperature": ["5.0"],
                           "BuildUpVertex.AssocIPTracks": ["1"],
                           "BuildUpVertex.AssocIPTracksChi2RatioSecToPri": ["2."],   # chi2 ratio to decide if assoc track to IP or SVX
                           "BuildUpVertex.AssocIPTracksMinDist": ["0.15"],           # min 3D dist to associate IP tracks to SVX
                           "BuildUpVertex.MassThreshold": ["10."],                  # vertex mass threshold
                           "BuildUpVertex.MaxChi2ForDistOrder": ["1."],
                           "BuildUpVertex.MinDistFromIP": ["0.15"],                  # 3d min dist for SVX seed -- works only with V0s!
                           "BuildUpVertex.MaxDistFromIP": ["50."],                  # 3d max dist for SVX seed -- works only with V0s!
                           "BuildUpVertex.PrimaryChi2Threshold": ["25."],
                           "BuildUpVertex.SecondaryChi2Threshold": ["10."],         # max x2 of track in SVX, try 10 or 20 then

                           "BuildUpVertex.TrackMaxD0": ["2.5"],
                           "BuildUpVertex.TrackMaxD0Err": ["1."],
                           #"BuildUpVertex.TrackMinD0Sig": ["2."],
                           "BuildUpVertex.TrackMaxZ0": ["3.5"],
                           "BuildUpVertex.TrackMaxZ0Err": ["1."],
                           #"BuildUpVertex.TrackMinZ0Sig": ["2."],
                           "BuildUpVertex.TrackMinR0": ["0.0"],
                           "BuildUpVertex.TrackMinPt": ["0.5"],
                           "BuildUpVertex.TrackMinD0Z0Sig": ["0."],
                           "BuildUpVertex.TrackMaxD0Z0Sig": ["999999999."],

                           "BuildUpVertex.UseAVF": ["true"],
                           "BuildUpVertex.UseV0Selection": ["1"],
                           "BuildUpVertex.V0VertexCollectionName": ["BuildUpVertices_V0"],
                           "BuildUpVertexCollectionName": ["BuildUpVertices"],
                           "MCPCollection": ["MCParticle"],
                           "MCPFORelation": ["RecoMCTruthLink"],
                           "MagneticField": ["5"],
                           "PFOCollection": ["PFOfromTracks_cone"],

                           "PrimaryVertexCollectionName": ["PrimaryVertices"],
                           "PrimaryVertexFinder.BeamspotConstraint": ["1"],
                           "PrimaryVertexFinder.BeamspotSmearing": ["false"],
                           "PrimaryVertexFinder.Chi2Threshold": ["25."],            #to check primary tracks number

                           "PrimaryVertexFinder.TrackMaxD0": ["0.2"],
                           "PrimaryVertexFinder.TrackMaxZ0": ["0.2"],
                           "PrimaryVertexFinder.TrackMaxD0Err": ["1."],
                           "PrimaryVertexFinder.TrackMaxZ0Err": ["1."],
                           "PrimaryVertexFinder.TrackMinD0Z0Sig": ["0.0"],  #constraints on R0/sigma(R0)
                           "PrimaryVertexFinder.TrackMaxD0Z0Sig": ["5.0"],

                           "PrintEventNumber": ["1"],
                           "ReadSubdetectorEnergies": ["0"],
                           "TrackHitOrdering": ["2"],
                           "UpdateVertexRPDaughters": ["0"],
                           "UseMCP": ["0"]
                           }
