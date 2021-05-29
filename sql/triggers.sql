---#############################################################################################################################################
create or replace function notify_message() returns trigger
language plpgsql as $$
declare
    notify_id notifications.notification_id%type;
    users_c cursor for
        select distinct sender_id 
        from messages
        where auction_id = new.auction_id
        and sender_id != new.sender_id;
    owner_id auctions.auctioneer_id%type;
    present boolean := false;
begin
    select auctioneer_id into owner_id
    from auctions
    where auction_id=new.auction_id;

    for user_row in users_c
    loop
        insert into notifications(title, body, send_date, receiver_id)
            values('NEW MESSAGE', 'There is a new message in auction ' || new.auction_id, current_timestamp, user_row.sender_id)
            returning notification_id into notify_id;
        
        insert into message_notifications(notification_id, message_id, auction_id)
            values(notify_id, new.message_id, new.auction_id);
        
        present := present or user_row.sender_id = owner_id;

    end loop;
    if not present and owner_id != new.sender_id then
        insert into notifications(title, body, send_date, receiver_id)
            values('NEW MESSAGE', 'There is a new message in auction ' || new.auction_id, current_timestamp, owner_id)
            returning notification_id into notify_id;
        
        insert into message_notifications(notification_id, message_id, auction_id)
            values(notify_id, new.message_id, new.auction_id);
    end if;
	return null;
end;
$$;

create trigger notify_message_trigger
after insert on messages
for each row 
execute procedure notify_message();
---#############################################################################################################################################

---#############################################################################################################################################
create or replace function notify_bidding() returns trigger
language plpgsql as $$
declare
    notify_id notifications.notification_id%type;
    users_c cursor for
    select distinct bidder_id
    from biddings
    where auction_id = new.auction_id
    and bidder_id != new.bidder_id;
begin

    for user_row in users_c
    loop
        insert into notifications (title, body, send_date, receiver_id)
            values ('NEW TOP BID', 'There is a new top bid in auction ' || new.auction_id, current_timestamp, user_row.bidder_id)
            returning notification_id into notify_id;
        insert into bidding_notifications (notification_id, bidding_id, auction_id)
            values (notify_id, new.bidding_id, new.auction_id);

    end loop;

    return null;
end;
$$;
---#############################################################################################################################################

create trigger notify_bidding_trigger
after insert on biddings
for each row 
execute procedure notify_bidding();
---#############################################################################################################################################

---#############################################################################################################################################
create or replace function add_history() returns trigger 
language plpgsql as $$
begin
    insert into auction_history (description, title, modified_date, auction_id)
        values (old.description, old.title, current_timestamp, old.auction_id);

    return new;
end;
$$;

create trigger add_history_trigger
after update of title, description
on auctions
for each row
execute procedure add_history();
---#############################################################################################################################################

---#############################################################################################################################################
create or replace procedure update_winning_bet() language plpgsql as $$

end;
$$;

create trigger update_winning_bet() language plpgsql as $$

end;
$$;
---#############################################################################################################################################
