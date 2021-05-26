CREATE TABLE leilao (
	leilaoid		 BIGINT DEFAULT 0,
	precominimo	 DOUBLE PRECISION NOT NULL DEFAULT 0,
	titulo		 VARCHAR(64) UNIQUE NOT NULL,
	descricao	 VARCHAR(1024),
	data_fim		 TIMESTAMP NOT NULL,
	data_criacao	 TIMESTAMP NOT NULL,
	artigoid		 BIGINT NOT NULL,
	artigonome	 VARCHAR(64) NOT NULL,
	utilizador_userid BIGINT NOT NULL DEFAULT 0,
	PRIMARY KEY(leilaoid)
);

CREATE TABLE licitacao (
	licitacaoid	 BIGINT DEFAULT 0,
	valor		 DOUBLE PRECISION NOT NULL,
	data		 TIMESTAMP NOT NULL,
	utilizador_userid BIGINT DEFAULT 0,
	leilao_leilaoid	 BIGINT DEFAULT 0,
	PRIMARY KEY(licitacaoid,utilizador_userid,leilao_leilaoid)
);

CREATE TABLE utilizador (
	userid	 BIGINT DEFAULT 0,
	email	 VARCHAR(64) UNIQUE NOT NULL,
	password VARCHAR(32) NOT NULL,
	username VARCHAR(16) UNIQUE NOT NULL,
	nome	 VARCHAR(128) NOT NULL,
	PRIMARY KEY(userid)
);

CREATE TABLE mensagem_notificacao_mural (
	mensagemid			 BIGINT,
	corpo			 VARCHAR(512) NOT NULL,
	data				 TIMESTAMP NOT NULL,
	leilao_leilaoid		 BIGINT NOT NULL DEFAULT 0,
	utilizador_userid		 BIGINT NOT NULL DEFAULT 0,
	notificacao_titulo		 VARCHAR(64) NOT NULL,
	notificacao_corpo		 VARCHAR(512) NOT NULL,
	notificacao_data_envio	 TIMESTAMP NOT NULL,
	notificacao_data_visualizacao TIMESTAMP,
	notificacao_utilizador_userid BIGINT NOT NULL DEFAULT 0
);

CREATE TABLE historico (
	historicoid	 BIGINT,
	descricao	 VARCHAR(1024),
	titulo		 VARCHAR(64) NOT NULL,
	data_alteracao	 TIMESTAMP NOT NULL,
	leilao_leilaoid BIGINT DEFAULT 0,
	PRIMARY KEY(historicoid,leilao_leilaoid)
);

CREATE TABLE notificacao_licitacao (
	leilao_leilaoid		 BIGINT DEFAULT 0,
	notificacao_titulo		 VARCHAR(64) NOT NULL,
	notificacao_corpo		 VARCHAR(512) NOT NULL,
	notificacao_data_envio	 TIMESTAMP NOT NULL,
	notificacao_data_visualizacao TIMESTAMP,
	notificacao_utilizador_userid BIGINT NOT NULL DEFAULT 0
);

ALTER TABLE leilao ADD CONSTRAINT leilao_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk1 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk2 FOREIGN KEY (leilao_leilaoid) REFERENCES leilao(leilaoid);
ALTER TABLE mensagem_notificacao_mural ADD CONSTRAINT mensagem_notificacao_mural_fk1 FOREIGN KEY (leilao_leilaoid) REFERENCES leilao(leilaoid);
ALTER TABLE mensagem_notificacao_mural ADD CONSTRAINT mensagem_notificacao_mural_fk2 FOREIGN KEY (utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE mensagem_notificacao_mural ADD CONSTRAINT mensagem_notificacao_mural_fk3 FOREIGN KEY (notificacao_utilizador_userid) REFERENCES utilizador(userid);
ALTER TABLE historico ADD CONSTRAINT historico_fk1 FOREIGN KEY (leilao_leilaoid) REFERENCES leilao(leilaoid);
ALTER TABLE notificacao_licitacao ADD CONSTRAINT notificacao_licitacao_fk1 FOREIGN KEY (leilao_leilaoid) REFERENCES leilao(leilaoid);
ALTER TABLE notificacao_licitacao ADD CONSTRAINT notificacao_licitacao_fk2 FOREIGN KEY (notificacao_utilizador_userid) REFERENCES utilizador(userid);

