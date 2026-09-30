#### MCParticle
MCP  = "MCParticle"
MCPP = "MCPhysicsParticle"

########### TRACKER

#### SimTrackerHit
VXDB_s = "VertexBarrelCollection"
VXDE_s = "VertexEndcapCollection"
ITDB_s = "InnerTrackerBarrelCollection"
ITDE_s = "InnerTrackerEndcapCollection"
OTDB_s = "OuterTrackerBarrelCollection"
OTDE_s = "OuterTrackerEndcapCollection"
ALL_sim = "SimHitsCollection"

#### TrackerHitPlane
VXDB_d = "VertexBarrel_digi"
VXDE_d = "VertexEndcap_digi"
ITDB_d = "InnerTrackerBarrel_digi"
ITDE_d = "InnerTrackerEndcap_digi"
OTDB_d = "OuterTrackerBarrel_digi"
OTDE_d = "OuterTrackerEndcap_digi"
ALL_digit = "HitsCollection"

#### Track
TRK_RAW     = "AllTracks"
TRK_ACTS    = "SiTracks"
TRK_FILTER  = "SiTracks_Filtered"
TRK_REFIT   = "SiTracks_Refitted"
TRK_MC      = "MCParticle_Tracks"
TRK_TRUTH   = "TruthTrk"

#### Tracks after cone filter
TRK_RAW_c     = "AllTracks_cone"
TRK_ACTS_c    = "SiTracks_cone"
TRK_FILTER_c  = "SiTracks_Filtered_cone"
TRK_REFIT_c   = "SiTracks_Refitted_cone"
TRK_MC_cr    = "MCParticle_Tracks_cone" # Track to MCParticle relation collection
TRK_REFIT_cr = "SiTracks_Refitted_conerel" # Refit Track to MCParticle relation collection Name--

#### LCRelation
VXDB_r = "VertexBarrel_rel"
VXDE_r = "VertexEndcap_rel"
ITDB_r = "InnerTrackerBarrel_rel"
ITDE_r = "InnerTrackerEndcap_rel"
OTDB_r = "OuterTrackerBarrel_rel"
OTDE_r = "OuterTrackerEndcap_rel"

TRK_MC_r    = "MCParticle_Tracks" # Track to MCParticle relation collection
TRK_REFIT_r = "SiTracks_Refitted_rel" # Refit Track to MCParticle relation collection Name--

#### Trk cone filtered hits
VXDB_c = "VertexBarrel_cone"
VXDE_c = "VertexEndcap_cone"
ITDB_c = "InnerTrackerBarrel_cone"
ITDE_c = "InnerTrackerEndcap_cone"
OTDB_c = "OuterTrackerBarrel_cone"
OTDE_c = "OuterTrackerEndcap_cone"
VXDB_cs = "VertexBarrelCollection_cone"
VXDE_cs = "VertexEndcapCollection_cone"
ITDB_cs = "InnerTrackerBarrelCollection_cone"
ITDE_cs = "InnerTrackerEndcapCollection_cone"
OTDB_cs = "OuterTrackerBarrelCollection_cone"
OTDE_cs = "OuterTrackerEndcapCollection_cone"
VXDB_cr = "VertexBarrel_conerel"
VXDE_cr = "VertexEndcap_conerel"
ITDB_cr = "InnerTrackerBarrel_conerel"
ITDE_cr = "InnerTrackerEndcap_conerel"
OTDB_cr = "OuterTrackerBarrel_conerel"
OTDE_cr = "OuterTrackerEndcap_conerel"

########## CALORIMETER

#### SimCalorimeterHit
ECB_s = "ECalBarrelCollection"
ECE_s = "ECalEndcapCollection"
HCB_s = "HCalBarrelCollection"
HCE_s = "HCalEndcapCollection"
YDB_s = "YokeBarrelCollection" 
YDE_s = "YokeEndcapCollection"

#### CalorimeterHit
ECB_d = "ECalBarrel_digi"
ECE_d = "ECalEndcap_digi"
HCB_d = "HCalBarrel_digi"
HCE_d = "HCalEndcap_digi"
MuD_d = "Muon_digi"

#### LCRelation
CALO_r = "CaloHits_rel"
MUON_r = "MuonHits_rel"

#### Cluster
CLUSTER = "PandoraClusters"

#### ReconstructedParticle
PFO     = "PandoraPFOs"
PFO_sel = "SelectedPandoraPFOs"
JET     = "JetOut"

#### Vertex
VTX_start = "PandoraStartVertices"
