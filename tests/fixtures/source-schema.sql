-- HTTP test-only dataset contract. Production importer schema is tested separately.
PRAGMA foreign_keys=ON;
CREATE TABLE sources(id TEXT PRIMARY KEY,path TEXT,original_path TEXT,sha256 TEXT,bytes INTEGER,media_type TEXT,kind TEXT,status TEXT,detail TEXT);
CREATE TABLE conversations(id TEXT PRIMARY KEY,native_id TEXT,title TEXT,source_id TEXT REFERENCES sources(id),locator TEXT,current_node TEXT,create_time TEXT,update_time TEXT,metadata_json TEXT);
CREATE TABLE messages(id TEXT PRIMARY KEY,conversation_id TEXT REFERENCES conversations(id),native_id TEXT,parent_id TEXT,role TEXT,text TEXT,content_sha256 TEXT,source_id TEXT REFERENCES sources(id),locator TEXT,create_time TEXT,branch_status TEXT,raw_json TEXT);
CREATE TABLE nodes(conversation_id TEXT REFERENCES conversations(id),native_id TEXT,parent_id TEXT,children_json TEXT,has_message INTEGER,on_current_branch INTEGER,PRIMARY KEY(conversation_id,native_id));
CREATE TABLE documents(id TEXT PRIMARY KEY,source_id TEXT REFERENCES sources(id),title TEXT,text TEXT,extractor TEXT,status TEXT);
CREATE TABLE refs(id TEXT PRIMARY KEY,message_id TEXT REFERENCES messages(id),reference TEXT,kind TEXT,resolution TEXT);
CREATE TABLE decisions(id TEXT PRIMARY KEY,message_id TEXT REFERENCES messages(id),kind TEXT,status TEXT,excerpt TEXT,method TEXT);
CREATE TABLE coverage(id TEXT PRIMARY KEY,status TEXT,scope TEXT,detail TEXT);
CREATE TABLE source_positions(message_id TEXT PRIMARY KEY REFERENCES messages(id),source_id TEXT REFERENCES sources(id),physical_lf_line INTEGER,utf8_byte_start INTEGER,utf8_byte_end INTEGER,raw_record_sha256 TEXT,legacy_locator TEXT,legacy_native_id TEXT,native_ordinal INTEGER,sequence_semantics TEXT,mapping_basis TEXT,decision_receipt TEXT);
CREATE VIRTUAL TABLE search_index USING fts5(id UNINDEXED,kind UNINDEXED,title,text,tokenize='unicode61 remove_diacritics 2');
