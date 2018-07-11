-- Adminer 4.6.3-dev PostgreSQL dump

\connect "dej9a2c44240dk";

DROP TABLE IF EXISTS "checkins";
DROP SEQUENCE IF EXISTS checkins_id_seq;
CREATE SEQUENCE checkins_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."checkins" (
    "id" integer DEFAULT nextval('checkins_id_seq') NOT NULL,
    "location_id" character varying,
    "user_id" integer,
    "comment" character varying,
    CONSTRAINT "checkins_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "checkins_location_id_fkey" FOREIGN KEY (location_id) REFERENCES zips(zip) NOT DEFERRABLE,
    CONSTRAINT "checkins_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) NOT DEFERRABLE
) WITH (oids = false);


DROP TABLE IF EXISTS "users";
DROP SEQUENCE IF EXISTS users_id_seq;
CREATE SEQUENCE users_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."users" (
    "id" integer DEFAULT nextval('users_id_seq') NOT NULL,
    "name" character varying NOT NULL,
    "password" character varying NOT NULL,
    CONSTRAINT "users_name_key" UNIQUE ("name"),
    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


DROP TABLE IF EXISTS "zips";
CREATE TABLE "public"."zips" (
    "zip" character varying NOT NULL,
    "city" character varying NOT NULL,
    "state" character varying NOT NULL,
    "latitude" numeric NOT NULL,
    "longitude" numeric NOT NULL,
    "population" integer NOT NULL,
    CONSTRAINT "zips_pkey" PRIMARY KEY ("zip")
) WITH (oids = false);


-- 2018-07-11 17:19:54.034197+00
