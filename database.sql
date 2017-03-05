--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

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
-- Name: cookies_by_username; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE cookies_by_username (
    user_name character varying(255) NOT NULL,
    cookie character varying(255) NOT NULL,
    creation_timestamp timestamp without time zone DEFAULT now()
);


ALTER TABLE public.cookies_by_username OWNER TO postgres;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE roles (
    role_name character varying(255) NOT NULL,
    creation_timestamp timestamp without time zone DEFAULT now()
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE user_roles (
    user_name character varying(255) NOT NULL,
    role_name character varying(255) NOT NULL,
    creation_timestamp timestamp without time zone DEFAULT now()
);


ALTER TABLE public.user_roles OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE users (
    user_name character varying(255) NOT NULL,
    pass_hash character varying(255) NOT NULL,
    creation_timestamp timestamp without time zone
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Data for Name: cookies_by_username; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY cookies_by_username (user_name, cookie, creation_timestamp) FROM stdin;
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
example_user@gmail.com	$2b$12$ZIdbdGkpxieMSJYI7YV.ReuNf201ysng6iiQXIHGXDZUz9Zwh7g0C	\N
\.


--
-- Name: roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (role_name);


--
-- Name: user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (user_name, role_name);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_name);


--
-- Name: lookup_user_name_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY cookies_by_username
    ADD CONSTRAINT lookup_user_name_fk FOREIGN KEY (user_name) REFERENCES users(user_name) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: role_name_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_roles
    ADD CONSTRAINT role_name_fk FOREIGN KEY (role_name) REFERENCES roles(role_name) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_name_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY user_roles
    ADD CONSTRAINT user_name_fk FOREIGN KEY (user_name) REFERENCES users(user_name) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: cookies_by_username; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE cookies_by_username FROM PUBLIC;
REVOKE ALL ON TABLE cookies_by_username FROM postgres;
GRANT ALL ON TABLE cookies_by_username TO postgres;
GRANT ALL ON TABLE cookies_by_username TO simple_auth;


--
-- Name: roles; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE roles FROM PUBLIC;
REVOKE ALL ON TABLE roles FROM postgres;
GRANT ALL ON TABLE roles TO postgres;
GRANT ALL ON TABLE roles TO simple_auth;


--
-- Name: user_roles; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE user_roles FROM PUBLIC;
REVOKE ALL ON TABLE user_roles FROM postgres;
GRANT ALL ON TABLE user_roles TO postgres;
GRANT ALL ON TABLE user_roles TO simple_auth;


--
-- Name: users; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE users FROM PUBLIC;
REVOKE ALL ON TABLE users FROM postgres;
GRANT ALL ON TABLE users TO postgres;
GRANT ALL ON TABLE users TO simple_auth;


--
-- PostgreSQL database dump complete
--

