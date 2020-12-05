create table public.users (
	ID  SERIAL PRIMARY KEY,    
	name text,
	area integer,
	number_of_connects integer,
	first_seen timestamp,
	last_update timestamp default current_timestamp
);

create table public.inventory (
	username text,
	items text,
	last_update timestamp default current_timestamp
);
