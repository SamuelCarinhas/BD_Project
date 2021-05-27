
create or replace procedure notify_message() language plpgsql as $$
begin

    insert into 

end;
$$;

create or replace trigger notify_message_trigger() 
after insert on messages
for each row 
execute procedure notify_message();


create or replace procedure notify_bidding() language plpgsql as $$

end;
$$;

create or replace procedure add_history() language plpgsql as $$

end;
$$;

create or replace procedure update_winning_bet() language plpgsql as $$

end;
$$;

create or replace or replace function delete_books() returns trigger
language plpgsql
as $$

begin
delete from livros where livros.id_autor = old.id_autor;
return new;
end;
$$;

create trigger <nome>
before delete on autores 
for each row 
execute procedure <procedimento>();