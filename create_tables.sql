CREATE TABLE auctions (
	auction_id		 		BIGINT DEFAULT 0,
	min_price	 			DOUBLE PRECISION NOT NULL DEFAULT 0,
	title		 			VARCHAR(64) UNIQUE NOT NULL,
	description	 			VARCHAR(1024),
	end_date		 		TIMESTAMP NOT NULL,
	creation_date	 		TIMESTAMP NOT NULL,
	item_id		 			BIGINT NOT NULL,
	item_name	 			VARCHAR(64) NOT NULL,
	auctioneer_id 			BIGINT NOT NULL DEFAULT 0,
	PRIMARY KEY(auction_id)
);

CREATE TABLE biddings (
	bidding_id	 			BIGINT DEFAULT 0,
	money		 			DOUBLE PRECISION NOT NULL,
	date		 			TIMESTAMP NOT NULL,
	bidder_id 				BIGINT DEFAULT 0,
	auction_id	 			BIGINT DEFAULT 0,
	PRIMARY KEY(bidding_id, bidder_id, auction_id)
);

CREATE TABLE users (
	user_id	 				BIGINT DEFAULT 0,
	email	 				VARCHAR(64) UNIQUE NOT NULL,
	password 				VARCHAR(32) NOT NULL,
	username 				VARCHAR(16) UNIQUE NOT NULL,
	name	 				VARCHAR(128) NOT NULL,
	PRIMARY KEY(user_id)
);

CREATE TABLE messages (
	message_id			 	BIGINT,
	message_body			VARCHAR(512) NOT NULL,
	date				 	TIMESTAMP NOT NULL,
	auction_id			 	BIGINT NOT NULL DEFAULT 0,
	sender_id				BIGINT NOT NULL DEFAULT 0,
	notif_title				VARCHAR(64) NOT NULL,
	notif_body				VARCHAR(512) NOT NULL,
	notif_send_date			TIMESTAMP NOT NULL,
	notif_received_date		TIMESTAMP,
	notif_receiver_id		BIGINT NOT NULL DEFAULT 0,
	PRIMARY KEY(message_id)
);

CREATE TABLE auction_history (
	history_id	 			BIGINT,
	description	 			VARCHAR(1024),
	title		 			VARCHAR(64) NOT NULL,
	modified_date	 		TIMESTAMP NOT NULL,
	auction_id 				BIGINT DEFAULT 0,
	PRIMARY KEY(history_id, auction_id)
);

CREATE TABLE bidding_notification (
	auction_id		 		BIGINT DEFAULT 0,
	notif_title				VARCHAR(64) NOT NULL,
	notif_body				VARCHAR(512) NOT NULL,
	notif_send_date			TIMESTAMP NOT NULL,
	notif_received_date		TIMESTAMP,
	notif_receiver_id		BIGINT NOT NULL DEFAULT 0,
	PRIMARY KEY(auction_id)
);

ALTER TABLE auctions ADD CONSTRAINT auctions_fk1 FOREIGN KEY (auctioneer_id) REFERENCES users(user_id);
ALTER TABLE biddings ADD CONSTRAINT biddings_fk1 FOREIGN KEY (bidder_id) REFERENCES users(user_id);
ALTER TABLE biddings ADD CONSTRAINT biddings_fk2 FOREIGN KEY (auction_id) REFERENCES auctions(auction_id);
ALTER TABLE messages ADD CONSTRAINT messages_fk1 FOREIGN KEY (auction_id) REFERENCES auctions(auction_id);
ALTER TABLE messages ADD CONSTRAINT messages_fk2 FOREIGN KEY (sender_id) REFERENCES users(user_id);
ALTER TABLE messages ADD CONSTRAINT messages_fk3 FOREIGN KEY (notif_receiver_id) REFERENCES users(user_id);
ALTER TABLE auction_history ADD CONSTRAINT auction_history_fk1 FOREIGN KEY (auction_id) REFERENCES auctions(auction_id);
ALTER TABLE bidding_notification ADD CONSTRAINT bidding_notification_fk1 FOREIGN KEY (auction_id) REFERENCES auctions(auction_id);
ALTER TABLE bidding_notification ADD CONSTRAINT bidding_notification_fk2 FOREIGN KEY (notif_receiver_id) REFERENCES users(user_id);

CREATE INDEX ON auctions ((lower(description)));
CREATE INDEX ON auctions ((lower(item_name)));
CREATE INDEX ON auctions (item_id);

