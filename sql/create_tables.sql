CREATE TABLE auctions (
	auction_id		 		SERIAL UNIQUE,
	min_price	 			DOUBLE PRECISION NOT NULL DEFAULT 0,
	title		 			VARCHAR(64) UNIQUE NOT NULL,
	description	 			VARCHAR(1024),
	end_date		 		TIMESTAMP NOT NULL,
	creation_date	 		TIMESTAMP NOT NULL,
	item_id		 			VARCHAR(32) NOT NULL,
	item_name	 			VARCHAR(64) NOT NULL,
	item_description		VARCHAR(1024),
	auctioneer_id 			BIGINT NOT NULL,
	winning_bid				BIGINT,
	ended					BOOLEAN NOT NULL DEFAULT FALSE,
	PRIMARY KEY(auction_id)
);

CREATE TABLE biddings (
	bidding_id	 			SERIAL UNIQUE,
	money		 			DOUBLE PRECISION NOT NULL,
	date		 			TIMESTAMP NOT NULL,
	bidder_id 				BIGINT NOT NULL,
	auction_id	 			BIGINT NOT NULL,
	PRIMARY KEY(bidding_id)
);

CREATE TABLE users (
	user_id	 				SERIAL UNIQUE,
	email	 				VARCHAR(64) UNIQUE NOT NULL,
	password 				VARCHAR(64) NOT NULL,
	username 				VARCHAR(32) UNIQUE NOT NULL,
	PRIMARY KEY(user_id)
);

CREATE TABLE messages (
	message_id			 	SERIAL UNIQUE,
	body					VARCHAR(512) NOT NULL,
	date				 	TIMESTAMP NOT NULL,
	auction_id			 	BIGINT NOT NULL,
	sender_id				BIGINT NOT NULL,
	PRIMARY KEY(message_id)
);

CREATE TABLE auction_history (
	history_id	 			SERIAL UNIQUE,
	description	 			VARCHAR(1024),
	title		 			VARCHAR(64) NOT NULL,
	modified_date	 		TIMESTAMP NOT NULL,
	auction_id 				BIGINT NOT NULL,
	PRIMARY KEY(history_id)
);

CREATE TABLE bidding_notifications (
	notification_id			BIGINT NOT NULL,
	bidding_id				BIGINT NOT NULL,
	auction_id		 		BIGINT NOT NULL,
	PRIMARY KEY(notification_id)
);

CREATE TABLE message_notifications (
	notification_id			BIGINT NOT NULL,
	message_id				BIGINT NOT NULL,
	auction_id				BIGINT NOT NULL,
	PRIMARY KEY(notification_id)
);

CREATE TABLE notifications (
	notification_id			SERIAL UNIQUE,
	title		 			VARCHAR(64) NOT NULL,
	body		 			VARCHAR(512) NOT NULL,
	send_date	 			TIMESTAMP NOT NULL,
	received_date 			TIMESTAMP,
	receiver_id 			BIGINT NOT NULL DEFAULT 0,
	PRIMARY KEY(notification_id)
);

ALTER TABLE auctions ADD CONSTRAINT auctions_fk1 FOREIGN KEY (auctioneer_id) REFERENCES users(user_id);
ALTER TABLE auctions ADD CONSTRAINT auctions_fk2 FOREIGN KEY (winning_bid) REFERENCES biddings(bidding_id);
ALTER TABLE biddings ADD CONSTRAINT biddings_fk1 FOREIGN KEY (bidder_id) REFERENCES users(user_id);
ALTER TABLE biddings ADD CONSTRAINT biddings_fk2 FOREIGN KEY (auction_id) REFERENCES auctions(auction_id);
ALTER TABLE messages ADD CONSTRAINT messages_fk1 FOREIGN KEY (auction_id) REFERENCES auctions(auction_id);
ALTER TABLE messages ADD CONSTRAINT messages_fk2 FOREIGN KEY (sender_id) REFERENCES users(user_id);
ALTER TABLE auction_history ADD CONSTRAINT auction_history_fk1 FOREIGN KEY (auction_id) REFERENCES auctions(auction_id);
ALTER TABLE bidding_notifications ADD CONSTRAINT bidding_notifications_fk1 FOREIGN KEY (auction_id) REFERENCES auctions(auction_id);
ALTER TABLE bidding_notifications ADD CONSTRAINT bidding_notifications_fk2 FOREIGN KEY (notification_id) REFERENCES notifications(notification_id);
ALTER TABLE bidding_notifications ADD CONSTRAINT bidding_notifications_fk3 FOREIGN KEY (bidding_id) REFERENCES biddings(bidding_id);
ALTER TABLE notifications ADD CONSTRAINT notifications_fk1 FOREIGN KEY (receiver_id) REFERENCES users(user_id);
ALTER TABLE message_notifications ADD CONSTRAINT message_notifications_fk1 FOREIGN KEY (auction_id) REFERENCES auctions(auction_id);
ALTER TABLE message_notifications ADD CONSTRAINT message_notifications_fk2 FOREIGN KEY (notification_id) REFERENCES notifications(notification_id);
ALTER TABLE message_notifications ADD CONSTRAINT message_notifications_fk3 FOREIGN KEY (message_id) REFERENCES messages(message_id);

CREATE INDEX ON auctions ((lower(description)));
CREATE INDEX ON auctions ((lower(item_name)));
CREATE INDEX ON auctions (item_id);
