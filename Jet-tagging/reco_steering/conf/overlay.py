from Gaudi.Configuration import *
from Configurables import MarlinProcessorWrapper

from constants import *

######################################
#### Defines the following processors:
# OverlayFalse
# OverlayBIB
# OverlayTrimmed
# OverlayTest
# OverlayDigi 
######################################

#### Default values
INTEGRATION_times = [
        "VertexBarrelCollection",       "-0.5", "15", 
        "VertexEndcapCollection",       "-0.5", "15", 
        "InnerTrackerBarrelCollection", "-0.5", "15", 
        "InnerTrackerEndcapCollection", "-0.5", "15", 
        "OuterTrackerBarrelCollection", "-0.5", "15", 
        "OuterTrackerEndcapCollection", "-0.5", "15", 
        "ECalBarrelCollection",         "-0.5", "25", 
        "ECalEndcapCollection",         "-0.5", "25", 
        "HCalBarrelCollection",         "-0.5", "25", 
        "HCalEndcapCollection",         "-0.5", "25", 
        "YokeBarrelCollection",         "-0.5", "25", 
        "YokeEndcapCollection",         "-0.5", "25"]

BIB_PATH      = "/MuSIC10TeV/BIB_SIM/"
BIBMIN_FILES  = [ BIB_PATH + "mum_" + str(i) + ".slcio" for i in range(6) ]
BIBPLUS_FILES = [ BIB_PATH + "mup_" + str(i) + ".slcio" for i in range(6) ]
BIB_iPairs = BIB_PATH + "iPairs.slcio"
BIB_EVENTS = "13333" # +1 for ipairs

BIBTRIM_PATH  = "BIB_TRIM/"
BIBTRIM_FILES = [ BIBTRIM_PATH + "BIB_10T_MuSICV2_TrimMinus_00.slcio", BIBTRIM_PATH + "BIB_10T_MuSICV2_TrimMinus_01.slcio", BIBTRIM_PATH + "BIB_10T_MuSICV2_TrimPlus_00.slcio", BIBTRIM_PATH + "BIB_10T_MuSICV2_TrimPlus_01.slcio" ] 
BIBTRIM_iPairs = BIBTRIM_PATH + "BIB_10T_MuSICV2_TrimiPairs.slcio"
BIBTRIM_EVENTS = "5" # +1 for ipairs

#### Processors
OverlayFalse = MarlinProcessorWrapper("OverlayFalse")
OverlayFalse.OutputLevel = INFO
OverlayFalse.ProcessorType = "OverlayTimingGeneric"
OverlayFalse.Parameters = {
    "BackgroundFileNames": ["/dev/null"],
    "Collection_IntegrationTimes": INTEGRATION_times, 
    "Delta_t": ["1"],
    "MCParticleCollectionName": [ MCP ],
    "MCPhysicsParticleCollectionName": [ MCPP ],
    "MergeMCParticles": ["false"],
    "NBunchtrain": ["0"],
    "NumberBackground": ["0."],
    "PhysicsBX": ["1"],
    "Poisson_random_NOverlay": ["false"],
    "RandomBx": ["false"],
    "TPCDriftvelocity": ["0.05"]
}

OverlayBIB = MarlinProcessorWrapper("OverlayBIB")
OverlayBIB.OutputLevel = INFO
OverlayBIB.ProcessorType = "OverlayTimingGeneric"
OverlayBIB.Parameters = {
    "AllowReusingBackgroundFiles": ["false"],
    "BackgroundFileNames": BIBMIN_FILES + BIBPLUS_FILES + [BIB_iPairs],
    "Collection_IntegrationTimes": INTEGRATION_times,
    "Delta_t": ["1"],
    "MCParticleCollectionName": [ MCP ],
    "MCPhysicsParticleCollectionName": [ MCPP ],
    "MergeMCParticles": ["false"],
    "NBunchtrain": ["1"],
    "NumberBackground": [ BIB_EVENTS ],
    "PhysicsBX": ["1"],
    "Poisson_random_NOverlay": ["false"],
    "RandomBx": ["false"],
    "StartBackgroundFileIndex": ["0"],
    "TPCDriftvelocity": ["0.05"],
    "ProcessMCContribution" : [ "true"]
}

OverlayTrimmed = MarlinProcessorWrapper("OverlayTrimmed")
OverlayTrimmed.OutputLevel = INFO
OverlayTrimmed.ProcessorType = "OverlayTimingGeneric"
OverlayTrimmed.Parameters = {
    "AllowReusingBackgroundFiles": ["false"],
    "BackgroundFileNames": BIBTRIM_FILES + [BIBTRIM_iPairs],
    "Collection_IntegrationTimes": INTEGRATION_times, 
    "Delta_t": ["1"],
    "MCParticleCollectionName": [ MCP ],
    "MCPhysicsParticleCollectionName": [ MCPP ],
    "MergeMCParticles": ["false"],
    "NBunchtrain": ["1"],
    "NumberBackground": [ BIBTRIM_EVENTS ],
    "PhysicsBX": ["1"],
    "Poisson_random_NOverlay": ["false"],
    "RandomBx": ["false"],
    "StartBackgroundFileIndex": ["0"],
    "TPCDriftvelocity": ["0.05"],
    "ProcessMCContribution" : [ "false "]
}

OverlayTrk = MarlinProcessorWrapper("OverlayTrk")
OverlayTrk.OutputLevel = INFO
OverlayTrk.ProcessorType = "OverlayTimingGeneric"
OverlayTrk.Parameters = {
    "AllowReusingBackgroundFiles": ["false"],
    "BackgroundFileNames": ["BIB_10T_MuSICV2_Trimmed_TRK.slcio"],
    "Collection_IntegrationTimes": INTEGRATION_times,
    "Delta_t": ["1"],
    "MCParticleCollectionName": [ MCP ],
    "MCPhysicsParticleCollectionName": [ MCPP ],
    "MergeMCParticles": ["false"],
    "NBunchtrain": ["1"],
    "NumberBackground": [ "1" ],
    "PhysicsBX": ["1"],
    "Poisson_random_NOverlay": ["false"],
    "RandomBx": ["false"],
    "StartBackgroundFileIndex": ["0"],
    "TPCDriftvelocity": ["0.05"],
    "ProcessMCContribution" : [ "false "]
}


OverlayDigi = MarlinProcessorWrapper("OverlayDigi")
OverlayDigi.OutputLevel = INFO
OverlayDigi.ProcessorType = "OverlayTimingGeneric"
OverlayDigi.Parameters = {
    "AllowReusingBackgroundFiles": ["false"],
    "BackgroundFileNames": ["/MuSIC10TeV/BIB_DIGI/BIB_digi.slcio"],
    "Collection_IntegrationTimes": INTEGRATION_times,
    "Delta_t": ["1"],
    "MCParticleCollectionName": [ MCP ],
    "MCPhysicsParticleCollectionName": [ MCPP ],
    "MergeMCParticles": ["false"],
    "NBunchtrain": ["1"],
    "NumberBackground": [ "1" ],
    "PhysicsBX": ["1"],
    "Poisson_random_NOverlay": ["false"],
    "RandomBx": ["false"],
    "StartBackgroundFileIndex": ["0"],
    "TPCDriftvelocity": ["0.05"],
    "ProcessMCContribution" : [ "false "]
}


