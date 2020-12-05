create table public.users (
	ID  SERIAL PRIMARY KEY,    
	name text,
	area integer,
	number_of_connects integer
);

create table public.inventory (
	username text,
	items text,
	last_update timestamp default current_timestamp
);
