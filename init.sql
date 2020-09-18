CREATE TABLE public.account(
	id SERIAL PRIMARY KEY,
	name varchar NOT NULL
);

ALTER TABLE public.account OWNER TO postgres;
