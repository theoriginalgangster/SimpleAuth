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
    creation_timestamp timestamp without time zone
);


ALTER TABLE users OWNER TO postgres;

--
-- Data for Name: cookies_by_username; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY cookies_by_username (user_name, cookie, creation_timestamp) FROM stdin;
\.


--
-- Data for Name: g_apptokens_by_email_address; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY g_apptokens_by_email_address (email_address, g_apptoken, creation_timestamp) FROM stdin;
zndr.k.94@gmail.com	g_plrvgjvixrotrewwmgdpyvhnungxh	2017-04-03 00:15:02.074455
\.


--
-- Data for Name: google_users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY google_users (email_address, creation_timestamp, last_login) FROM stdin;
new_guy@gmail.com	2017-04-02 22:51:38.270002	2017-04-02 22:51:44.461903
zndr.k.94@gmail.com	2017-04-02 22:48:48.7878	2017-04-03 00:15:03.257574
example_user@gmail.com	2017-04-03 00:22:08.614517	2017-04-03 00:22:36.4561
\.


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
example_user@gmail.com	$2b$12$yzf3dfy8hj.dnuJ7nU9N/u69YAqONlaKUuUBHiLc8Px6pW9lx8QAu	\N
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
-- Name: cookies_by_username lookup_user_name_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY cookies_by_username
    ADD CONSTRAINT lookup_user_name_fk FOREIGN KEY (user_name) REFERENCES users(user_name) ON UPDATE CASCADE ON DELETE CASCADE;


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

