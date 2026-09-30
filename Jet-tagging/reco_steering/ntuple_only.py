"""ntuple_only.py -- regenerate LCTuple ntuples from EXISTING reco slcio.

The full reco_steer_jets.py chain (digitisation, CKF tracking, Pandora,
vertexing) is by far the expensive part, and none of it is needed to rewrite the
ntuple: every collection LCTuple reads (JetOut_kt, SiTracks_Refitted, GenJet_VLC,
MCParticle, BuildUpVertices*) is already persisted in recoSig/*.slcio.

This steering reads a reco file and runs only the ntuple processors, so a fix to
LCTuple can be rolled out without re-running reconstruction.

NOTE on where the trees land: LCTuple::init() does a bare `new TTree(name())`
without calling AIDAProcessor::tree(this), so the tree attaches to whatever TFile
is current at init time. MyJetAnalyzer opens that file, so it MUST stay in the
algorithm list and MUST be scheduled before the LCTuple processors -- otherwise
the trees are created in gROOT and silently never written.

Usage:
  k4run ntuple_only.py --input reco_xxx.slcio --tupleout tuples_xxx.root [--nevt N]
"""
import os
from Gaudi.Configuration import *
from Configurables import LcioEvent, EventDataSvc, MarlinProcessorWrapper
from k4FWCore.parseArgs import parser

parser.add_argument("--input", type=str, required=True, help="input reco slcio")
parser.add_argument("--tupleout", type=str, default="tuples.root", help="output ROOT ntuple")
parser.add_argument("--nevt", type=int, default=-1, help="number of events (-1 = all)")
the_args = parser.parse_known_args()[0]

algList = []
evtsvc = EventDataSvc()

read = LcioEvent()
read.OutputLevel = INFO
read.Files = [the_args.input]
algList.append(read)

# Opens the TFile that the LCTuple trees attach to -- see note above.
MyJetAnalyzer = MarlinProcessorWrapper("MyJetAnalyzer")
MyJetAnalyzer.OutputLevel = INFO
MyJetAnalyzer.ProcessorType = "JetAnalyzer"
MyJetAnalyzer.Parameters = {
    "GenJetCollection": ["GenJet_VLC"],
    "MCParticleCollectionName": ["MCParticle"],
    "OutputRootFileName": [the_args.tupleout],
    "RECOParticleCollectionName": ["PandoraPFOs"],
    "ProcessName": ["dijet"],
    "RecoJetCollection": ["BuildUpVertices_RP"],
    "doDiBosonChecks": ["false"],
    "fillMEInfo": ["true"],
}
algList.append(MyJetAnalyzer)

# The LCTuple instances, identical to conf/ntuple.py
JET_kt_LCTuple = MarlinProcessorWrapper("JET_kt")
JET_kt_LCTuple.OutputLevel = INFO
JET_kt_LCTuple.ProcessorType = "LCTuple"
JET_kt_LCTuple.Parameters = {
    "MCParticleCollection": ['  '],
    "RecoParticleCollection": ["SelectedPandoraPFOs"],
    "JetCollection": ["JetOut_kt"],
    "WriteJetCollectionParameters": ["true"],
    "JetCollectionDaughtersParameters": ["true"],
    "JetCollectionExtraParameters": ["false"],
    "JetCollectionTaggingParameters": ["false"],
    "VertexCollection": ["BuildUpVertices"],
}
algList.append(JET_kt_LCTuple)

TrueJets = MarlinProcessorWrapper("TrueJets")
TrueJets.OutputLevel = INFO
TrueJets.ProcessorType = "LCTuple"
TrueJets.Parameters = {
    "MCParticleCollection": ["MCParticle"],
    "JetCollection": ["GenJet_VLC"],
    "WriteJetCollectionParameters": ["true"],
    "JetCollectionDaughtersParameters": ["true"],
    "JetCollectionExtraParameters": ["false"],
    "JetCollectionTaggingParameters": ["false"],
}
algList.append(TrueJets)

from Configurables import ApplicationMgr
ApplicationMgr(TopAlg=algList,
               EvtSel='NONE',
               EvtMax=the_args.nevt,
               ExtSvc=[evtsvc],
               OutputLevel=INFO)
