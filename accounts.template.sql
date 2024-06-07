
DELETE FROM public.profile;

DELETE FROM public.role;
ALTER SEQUENCE public.role_id_seq RESTART;
UPDATE public.role SET id = DEFAULT;

DELETE FROM public.account;
ALTER SEQUENCE public.account_id_seq RESTART;
UPDATE public.account SET id = DEFAULT;


INSERT INTO public.account (name, key, salt) VALUES ('admin', '@PASSWORD', '@SALT');

INSERT INTO public.account (name, key, salt) VALUES ('user', '@PASSWORD', '@SALT');

INSERT INTO public.role(name) VALUES('admin');
INSERT INTO public.role(name) VALUES('user');

INSERT INTO public.profile(role, account) VALUES(1, 1);
INSERT INTO public.profile(role, account) VALUES(2, 1);
INSERT INTO public.profile(role, account) VALUES(2, 2);
