--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.2
-- Dumped by pg_dump version 9.6.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: cookies_by_username; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE cookies_by_username (
    user_name character varying(255) NOT NULL,
    cookie character varying(255) NOT NULL,
    creation_timestamp timestamp without time zone DEFAULT now()
);


ALTER TABLE cookies_by_username OWNER TO postgres;

--
-- Name: g_apptokens_by_email_address; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE g_apptokens_by_email_address (
    email_address character varying(255) NOT NULL,
    g_apptoken character varying(255) NOT NULL,
    creation_timestamp timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE g_apptokens_by_email_address OWNER TO postgres;

--
-- Name: google_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE google_users (
    email_address character varying(255) NOT NULL,
    creation_timestamp timestamp without time zone DEFAULT now() NOT NULL,
    last_login timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE google_users OWNER TO postgres;

--
-- Name: notification_messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE notification_messages (
    id integer NOT NULL,
    sender character varying(255),
    recipient character varying(255),
    read boolean DEFAULT false NOT NULL,
    creation_timestamp timestamp without time zone DEFAULT now() NOT NULL,
    message text NOT NULL
);


ALTER TABLE notification_messages OWNER TO postgres;

--
-- Name: notification_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE notification_messages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE notification_messages_id_seq OWNER TO postgres;

--
-- Name: notification_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE notification_messages_id_seq OWNED BY notification_messages.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE roles (
    role_name character varying(255) NOT NULL,
    creation_timestamp timestamp without time zone DEFAULT now()
);


ALTER TABLE roles OWNER TO postgres;

--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE user_roles (
    user_name character varying(255) NOT NULL,
    role_name character varying(255) NOT NULL,
    creation_timestamp timestamp without time zone DEFAULT now()
);


ALTER TABLE user_roles OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE users (
    user_name character varying(255) NOT NULL,
    pass_hash character varying(255) NOT NULL,
    creation_timestamp timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE users OWNER TO postgres;

--
-- Name: notification_messages id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY notification_messages ALTER COLUMN id SET DEFAULT nextval('notification_messages_id_seq'::regclass);


--
-- Data for Name: cookies_by_username; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY cookies_by_username (user_name, cookie, creation_timestamp) FROM stdin;
example_user@gmail.com	ecqvepmfpwmzzmrqmcbcsvtwqwdrk	2017-04-05 21:46:05.243873
\.


--
-- Data for Name: g_apptokens_by_email_address; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY g_apptokens_by_email_address (email_address, g_apptoken, creation_timestamp) FROM stdin;
gitkit_user@gmail.com	g_gaixdslwzgxgjtldrypubssqhkbqs	2017-04-09 00:27:50.762661
\.


--
-- Data for Name: google_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY google_users (email_address, creation_timestamp, last_login) FROM stdin;
gitkit_user@gmail.com	2017-04-09 00:27:50.760632	2017-04-09 02:51:21.980328
\.


--
-- Data for Name: notification_messages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY notification_messages (id, sender, recipient, read, creation_timestamp, message) FROM stdin;
1	gitkit_user@gmail.com	example_user@gmail.com	t	2017-04-09 00:40:29.521555	Hey!
5	example_user@gmail.com	gitkit_user@gmail.com	t	2017-04-09 02:39:48.624602	test from example to gitkit_user
6	gitkit_user@gmail.com	example_user@gmail.com	t	2017-04-09 02:51:28.441219	some message
7	example_user@gmail.com	gitkit_user@gmail.com	t	2017-04-09 02:59:23.924954	message from me
2	example_user@gmail.com	gitkit_user@gmail.com	t	2017-04-09 00:40:29.521555	Hey again dude
3	gitkit_user@gmail.com	example_user@gmail.com	t	2017-04-09 00:47:19.335612	something
4	example_user@gmail.com	gitkit_user@gmail.com	t	2017-04-09 02:39:17.217249	something else
\.


--
-- Name: notification_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('notification_messages_id_seq', 7, true);


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY roles (role_name, creation_timestamp) FROM stdin;
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY user_roles (user_name, role_name, creation_timestamp) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY users (user_name, pass_hash, creation_timestamp) FROM stdin;
example_user@gmail.com	$2b$12$c2/nhQWTJB/iiyVnNi3sz.AI7Rt8P5v1kJFd0qHzRH568H2Rc.eJm	2017-04-09 00:22:53.093715
gitkit_user@gmail.com	GOOGLE_NO_PASS	2017-04-09 00:27:50.756996
\.


--
-- Name: g_apptokens_by_email_address google_cookies_by_email_address_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY g_apptokens_by_email_address
    ADD CONSTRAINT google_cookies_by_email_address_pkey PRIMARY KEY (email_address);


--
-- Name: google_users google_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY google_users
    ADD CONSTRAINT google_users_pkey PRIMARY KEY (email_address);


--
-- Name: notification_messages notification_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY notification_messages
    ADD CONSTRAINT notification_messages_pkey PRIMARY KEY (id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (role_name);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (user_name, role_name);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_name);


--
-- Name: g_apptokens_by_email_address google_cookies_by_email_address_email_address_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY g_apptokens_by_email_address
    ADD CONSTRAINT google_cookies_by_email_address_email_address_fkey FOREIGN KEY (email_address) REFERENCES google_users(email_address) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: google_users google_users_email_address_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY google_users
    ADD CONSTRAINT google_users_email_address_fkey FOREIGN KEY (email_address) REFERENCES users(user_name) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: cookies_by_username lookup_user_name_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY cookies_by_username
    ADD CONSTRAINT lookup_user_name_fk FOREIGN KEY (user_name) REFERENCES users(user_name) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: notification_messages notification_messages_recipient_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY notification_messages
    ADD CONSTRAINT notification_messages_recipient_fkey FOREIGN KEY (recipient) REFERENCES users(user_name) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: notification_messages notification_messages_sender_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY notification_messages
    ADD CONSTRAINT notification_messages_sender_fkey FOREIGN KEY (sender) REFERENCES users(user_name) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_roles role_name_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_roles
    ADD CONSTRAINT role_name_fk FOREIGN KEY (role_name) REFERENCES roles(role_name) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_roles user_name_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_roles
    ADD CONSTRAINT user_name_fk FOREIGN KEY (user_name) REFERENCES users(user_name) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: cookies_by_username; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE cookies_by_username TO simple_auth;


--
-- Name: g_apptokens_by_email_address; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE g_apptokens_by_email_address TO simple_auth;


--
-- Name: google_users; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE google_users TO simple_auth;


--
-- Name: notification_messages; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE notification_messages TO simple_auth;


--
-- Name: notification_messages_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE notification_messages_id_seq TO simple_auth;


--
-- Name: roles; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE roles TO simple_auth;


--
-- Name: user_roles; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE user_roles TO simple_auth;


--
-- Name: users; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE users TO simple_auth;


--
-- PostgreSQL database dump complete
--

