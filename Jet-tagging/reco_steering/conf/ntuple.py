from Gaudi.Configuration import *
from Configurables import MarlinProcessorWrapper

from constants import *
import os

MyLCTuple = MarlinProcessorWrapper("MyLCTuple")
MyLCTuple.OutputLevel = DEBUG
MyLCTuple.ProcessorType = "LCTuple"
MyLCTuple.Parameters = {
    "CalorimeterHitCollection": [],
    "ClusterCollection": [""],
    "FullSubsetCollections": [],
    "IsoLepCollection": [],
    #"JetCollection": ["JetOut_kt"],
    "JetCollection": ["FakeRemovedJets"],
    "JetCollectionDaughtersParameters": ["true"],
    "JetCollectionExtraParameters": ["false"],
    "JetCollectionTaggingParameters": ["false"],
    "LCRelationCollections": [],
    "LCRelationPrefixes": [],
    "LCRelationwithPFOCollections": [],
    "MCParticleCollection": [ "MCParticle" ],
    "MCParticleNotReco": [],
    "RecoParticleCollection": [ "PFOfromTracks_cone" ],
    "SimCalorimeterHitCollection": [],
    "SimTrackerHitCollection": [],
    "TrackCollection": [TRK_FILTER_c],
    "TrackerHitCollection": [],
    "VertexCollection": ['BuildUpVertices'],
    "WriteCalorimeterHitCollectionParameters": ["false"],
    "WriteClusterCollectionParameters": ["false"],
    "WriteIsoLepCollectionParameters": ["false"],
    "WriteJetCollectionParameters": ["false"],
    "WriteMCParticleCollectionParameters": ["false"],
    "WriteRecoParticleCollectionParameters": ["false"],
    "WriteSimCalorimeterHitCollectionParameters": ["false"],
    "WriteSimTrackerHitCollectionParameters": ["false"],
    "WriteTrackCollectionParameters": ["false"],
    "TrackCollectionStatesParameters": ["true"],
    "TrackCollectionExtraParameters": ["false"],
    "WriteTrackerHitCollectionParameters": ["false"],
    "WriteVertexCollectionParameters": ["false"],
    "WriteCaloClusterHits" : ["false"],
    "SelectNearbyTracks" : ["false"],
    "NearbyTracksSelectionRadius" : ["0.005"]
}

PrimaryVertices = MarlinProcessorWrapper("PrimaryVertices")
PrimaryVertices.OutputLevel = DEBUG
PrimaryVertices.ProcessorType = "LCTuple"
PrimaryVertices.Parameters = {
    #"RecoParticleCollection": [ "PrimaryVertices_RP" ],
    "JetCollection": ["PrimaryVertices_RP"],
    "JetCollectionDaughtersParameters": ["true"],
    "JetCollectionExtraParameters": ["false"],
    "JetCollectionTaggingParameters": ["false"],
    "VertexCollection": ["PrimaryVertices"]
}

BUVertices = MarlinProcessorWrapper("BUVertices")
BUVertices.OutputLevel = DEBUG
BUVertices.ProcessorType = "LCTuple"
BUVertices.Parameters = {
    #"RecoParticleCollection": [ "BuildUpVertices_RP" ],
    "JetCollection": ["BuildUpVertices_RP"],
    "WriteJetCollectionParameters": ["true"],
    "JetCollectionDaughtersParameters": ["true"],
    "JetCollectionExtraParameters": ["false"],
    "JetCollectionTaggingParameters": ["false"],
    "VertexCollection": ["BuildUpVertices"]
}

TrueJets = MarlinProcessorWrapper("TrueJets")
TrueJets.OutputLevel = DEBUG
TrueJets.ProcessorType = "LCTuple"
TrueJets.Parameters = {
    "MCParticleCollection": ["MCParticle"],
    "JetCollection": ["GenJet_VLC"],
    "WriteJetCollectionParameters": ["true"],
    "JetCollectionDaughtersParameters": ["true"],
    "JetCollectionExtraParameters": ["false"],
    "JetCollectionTaggingParameters": ["false"],
}

JET_kt_LCTuple = MarlinProcessorWrapper("JET_kt")
JET_kt_LCTuple.OutputLevel = INFO
JET_kt_LCTuple.ProcessorType = "LCTuple"
JET_kt_LCTuple.Parameters = {
    "MCParticleCollection": [ '  ' ],
    "RecoParticleCollection": ["SelectedPandoraPFOs"],
    "JetCollection": [ "JetOut_kt" ],
    "WriteJetCollectionParameters": ["true"],
    "JetCollectionDaughtersParameters": ["true"],
    "JetCollectionExtraParameters": ["false"],
    "JetCollectionTaggingParameters": ["false"],
    "VertexCollection": ["BuildUpVertices"]
}
