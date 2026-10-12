--
-- PostgreSQL database dump
--

\restrict AsCCqwGE4Rl6xDjgjoFKCHgb6H6X06TPW4JiJKcPSd7s8gCEA1eRqem5QNKqvQp

-- Dumped from database version 17.11
-- Dumped by pg_dump version 17.11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: tiendas_tienda; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.tiendas_tienda (id, slug, nombre, activa, fecha_creacion, banner, color_acento, color_destacado, color_primario, color_primario_hover, instagram, logo, whatsapp) VALUES (1, 'joyas-ye', 'Joyas Ye', true, '2026-09-27 04:09:50.774017+00', '', '', '', '', '', '', '', '');


--
-- Data for Name: agenda_bloquehorario; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.agenda_bloquehorario (id, fecha_creacion, fecha_edicion, dia_semana, hora_inicio, hora_fin, tienda_id, confirmacion_automatica, duracion_minutos, fecha, nombre, visitas_simultaneas) VALUES (1, '2026-09-27 04:33:39.647453+00', '2026-09-27 04:33:39.647465+00', 0, '10:00:00', '13:00:00', 1, NULL, NULL, NULL, '', NULL);
INSERT INTO public.agenda_bloquehorario (id, fecha_creacion, fecha_edicion, dia_semana, hora_inicio, hora_fin, tienda_id, confirmacion_automatica, duracion_minutos, fecha, nombre, visitas_simultaneas) VALUES (2, '2026-09-27 04:33:39.652258+00', '2026-09-27 04:33:39.652269+00', 0, '15:00:00', '18:00:00', 1, NULL, NULL, NULL, '', NULL);
INSERT INTO public.agenda_bloquehorario (id, fecha_creacion, fecha_edicion, dia_semana, hora_inicio, hora_fin, tienda_id, confirmacion_automatica, duracion_minutos, fecha, nombre, visitas_simultaneas) VALUES (3, '2026-09-27 04:33:39.657061+00', '2026-09-27 04:33:39.657073+00', 1, '10:00:00', '13:00:00', 1, NULL, NULL, NULL, '', NULL);
INSERT INTO public.agenda_bloquehorario (id, fecha_creacion, fecha_edicion, dia_semana, hora_inicio, hora_fin, tienda_id, confirmacion_automatica, duracion_minutos, fecha, nombre, visitas_simultaneas) VALUES (4, '2026-09-27 04:33:39.661484+00', '2026-09-27 04:33:39.661496+00', 1, '15:00:00', '18:00:00', 1, NULL, NULL, NULL, '', NULL);
INSERT INTO public.agenda_bloquehorario (id, fecha_creacion, fecha_edicion, dia_semana, hora_inicio, hora_fin, tienda_id, confirmacion_automatica, duracion_minutos, fecha, nombre, visitas_simultaneas) VALUES (5, '2026-09-27 04:33:39.665551+00', '2026-09-27 04:33:39.665562+00', 2, '10:00:00', '13:00:00', 1, NULL, NULL, NULL, '', NULL);
INSERT INTO public.agenda_bloquehorario (id, fecha_creacion, fecha_edicion, dia_semana, hora_inicio, hora_fin, tienda_id, confirmacion_automatica, duracion_minutos, fecha, nombre, visitas_simultaneas) VALUES (6, '2026-09-27 04:33:39.669196+00', '2026-09-27 04:33:39.669206+00', 2, '15:00:00', '18:00:00', 1, NULL, NULL, NULL, '', NULL);
INSERT INTO public.agenda_bloquehorario (id, fecha_creacion, fecha_edicion, dia_semana, hora_inicio, hora_fin, tienda_id, confirmacion_automatica, duracion_minutos, fecha, nombre, visitas_simultaneas) VALUES (7, '2026-09-27 04:33:39.673252+00', '2026-09-27 04:33:39.673263+00', 3, '10:00:00', '13:00:00', 1, NULL, NULL, NULL, '', NULL);
INSERT INTO public.agenda_bloquehorario (id, fecha_creacion, fecha_edicion, dia_semana, hora_inicio, hora_fin, tienda_id, confirmacion_automatica, duracion_minutos, fecha, nombre, visitas_simultaneas) VALUES (8, '2026-09-27 04:33:39.677737+00', '2026-09-27 04:33:39.677748+00', 3, '15:00:00', '18:00:00', 1, NULL, NULL, NULL, '', NULL);
INSERT INTO public.agenda_bloquehorario (id, fecha_creacion, fecha_edicion, dia_semana, hora_inicio, hora_fin, tienda_id, confirmacion_automatica, duracion_minutos, fecha, nombre, visitas_simultaneas) VALUES (9, '2026-09-27 04:33:39.681287+00', '2026-09-27 04:33:39.681297+00', 4, '10:00:00', '13:00:00', 1, NULL, NULL, NULL, '', NULL);
INSERT INTO public.agenda_bloquehorario (id, fecha_creacion, fecha_edicion, dia_semana, hora_inicio, hora_fin, tienda_id, confirmacion_automatica, duracion_minutos, fecha, nombre, visitas_simultaneas) VALUES (10, '2026-09-27 04:33:39.684478+00', '2026-09-27 04:33:39.684488+00', 4, '15:00:00', '18:00:00', 1, NULL, NULL, NULL, '', NULL);


--
-- Data for Name: agenda_configuracionagenda; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.agenda_configuracionagenda (id, fecha_creacion, fecha_edicion, duracion_minutos, visitas_por_bloque, anticipacion_minima_horas, ventana_maxima_dias, confirmacion_automatica, direccion, indicaciones, correo_notificaciones, token_feed, tienda_id) VALUES (1, '2026-09-27 04:33:39.633656+00', '2026-09-27 04:33:39.633676+00', 30, 1, 24, 30, false, '', '', '', 'REEMPLAZAR-AL-RESTAURAR-token-de-ejemplo', 1);


--
-- Data for Name: agenda_diabloqueado; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.django_content_type (id, app_label, model) VALUES (1, 'admin', 'logentry');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (2, 'auth', 'permission');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (3, 'auth', 'group');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (4, 'contenttypes', 'contenttype');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (5, 'sessions', 'session');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (6, 'usuarios', 'usuario');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (7, 'tiendas', 'tienda');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (8, 'clientes', 'aprobacionmayorista');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (9, 'agenda', 'visita');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (10, 'agenda', 'enviocorreo');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (11, 'agenda', 'bloquehorario');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (12, 'agenda', 'configuracionagenda');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (13, 'agenda', 'diabloqueado');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (14, 'tiendas', 'solicituddeacceso');


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (1, 'Can add log entry', 1, 'add_logentry');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (2, 'Can change log entry', 1, 'change_logentry');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (3, 'Can delete log entry', 1, 'delete_logentry');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (4, 'Can view log entry', 1, 'view_logentry');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (5, 'Can add permission', 2, 'add_permission');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (6, 'Can change permission', 2, 'change_permission');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (7, 'Can delete permission', 2, 'delete_permission');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (8, 'Can view permission', 2, 'view_permission');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (9, 'Can add group', 3, 'add_group');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (10, 'Can change group', 3, 'change_group');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (11, 'Can delete group', 3, 'delete_group');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (12, 'Can view group', 3, 'view_group');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (13, 'Can add content type', 4, 'add_contenttype');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (14, 'Can change content type', 4, 'change_contenttype');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (15, 'Can delete content type', 4, 'delete_contenttype');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (16, 'Can view content type', 4, 'view_contenttype');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (17, 'Can add session', 5, 'add_session');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (18, 'Can change session', 5, 'change_session');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (19, 'Can delete session', 5, 'delete_session');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (20, 'Can view session', 5, 'view_session');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (21, 'Can add usuario', 6, 'add_usuario');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (22, 'Can change usuario', 6, 'change_usuario');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (23, 'Can delete usuario', 6, 'delete_usuario');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (24, 'Can view usuario', 6, 'view_usuario');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (25, 'Can add tienda', 7, 'add_tienda');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (26, 'Can change tienda', 7, 'change_tienda');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (27, 'Can delete tienda', 7, 'delete_tienda');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (28, 'Can view tienda', 7, 'view_tienda');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (29, 'Can add aprobación mayorista', 8, 'add_aprobacionmayorista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (30, 'Can change aprobación mayorista', 8, 'change_aprobacionmayorista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (31, 'Can delete aprobación mayorista', 8, 'delete_aprobacionmayorista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (32, 'Can view aprobación mayorista', 8, 'view_aprobacionmayorista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (33, 'Can add visita', 9, 'add_visita');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (34, 'Can change visita', 9, 'change_visita');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (35, 'Can delete visita', 9, 'delete_visita');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (36, 'Can view visita', 9, 'view_visita');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (37, 'Can add envío de correo', 10, 'add_enviocorreo');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (38, 'Can change envío de correo', 10, 'change_enviocorreo');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (39, 'Can delete envío de correo', 10, 'delete_enviocorreo');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (40, 'Can view envío de correo', 10, 'view_enviocorreo');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (41, 'Can add bloque horario', 11, 'add_bloquehorario');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (42, 'Can change bloque horario', 11, 'change_bloquehorario');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (43, 'Can delete bloque horario', 11, 'delete_bloquehorario');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (44, 'Can view bloque horario', 11, 'view_bloquehorario');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (45, 'Can add configuración de agenda', 12, 'add_configuracionagenda');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (46, 'Can change configuración de agenda', 12, 'change_configuracionagenda');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (47, 'Can delete configuración de agenda', 12, 'delete_configuracionagenda');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (48, 'Can view configuración de agenda', 12, 'view_configuracionagenda');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (49, 'Can add día bloqueado', 13, 'add_diabloqueado');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (50, 'Can change día bloqueado', 13, 'change_diabloqueado');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (51, 'Can delete día bloqueado', 13, 'delete_diabloqueado');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (52, 'Can view día bloqueado', 13, 'view_diabloqueado');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (53, 'Can add solicitud de acceso', 14, 'add_solicituddeacceso');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (54, 'Can change solicitud de acceso', 14, 'change_solicituddeacceso');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (55, 'Can delete solicitud de acceso', 14, 'delete_solicituddeacceso');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (56, 'Can view solicitud de acceso', 14, 'view_solicituddeacceso');


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.django_migrations (id, app, name, applied) VALUES (1, 'tiendas', '0001_initial', '2026-09-26 20:07:18.606816+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (2, 'contenttypes', '0001_initial', '2026-09-26 20:07:18.61859+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (3, 'contenttypes', '0002_remove_content_type_name', '2026-09-26 20:07:18.630174+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (4, 'auth', '0001_initial', '2026-09-26 20:07:18.67567+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (5, 'auth', '0002_alter_permission_name_max_length', '2026-09-26 20:07:18.686593+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (6, 'auth', '0003_alter_user_email_max_length', '2026-09-26 20:07:18.692377+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (7, 'auth', '0004_alter_user_username_opts', '2026-09-26 20:07:18.703167+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (8, 'auth', '0005_alter_user_last_login_null', '2026-09-26 20:07:18.709609+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (9, 'auth', '0006_require_contenttypes_0002', '2026-09-26 20:07:18.715807+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (10, 'auth', '0007_alter_validators_add_error_messages', '2026-09-26 20:07:18.722127+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (11, 'auth', '0008_alter_user_username_max_length', '2026-09-26 20:07:18.733548+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (12, 'auth', '0009_alter_user_last_name_max_length', '2026-09-26 20:07:18.739735+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (13, 'auth', '0010_alter_group_name_max_length', '2026-09-26 20:07:18.753202+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (14, 'auth', '0011_update_proxy_permissions', '2026-09-26 20:07:18.762838+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (15, 'auth', '0012_alter_user_first_name_max_length', '2026-09-26 20:07:18.769437+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (16, 'usuarios', '0001_initial', '2026-09-26 20:07:18.832504+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (17, 'admin', '0001_initial', '2026-09-26 20:07:18.874259+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (18, 'admin', '0002_logentry_remove_auto_add', '2026-09-26 20:07:18.885248+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (19, 'admin', '0003_logentry_add_action_flag_choices', '2026-09-26 20:07:18.897475+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (20, 'clientes', '0001_initial', '2026-09-26 20:07:18.906188+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (21, 'clientes', '0002_initial', '2026-09-26 20:07:18.972742+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (22, 'sessions', '0001_initial', '2026-09-26 20:07:18.988578+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (23, 'agenda', '0001_initial', '2026-09-26 20:19:49.685394+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (24, 'agenda', '0002_alter_bloquehorario_options_and_more', '2026-09-26 21:14:34.591356+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (25, 'tiendas', '0002_tienda_banner_tienda_color_acento_and_more', '2026-09-27 04:08:07.941082+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (26, 'tiendas', '0003_solicituddeacceso', '2026-09-28 02:53:34.748028+00');


--
-- Name: agenda_bloquehorario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.agenda_bloquehorario_id_seq', 10, true);


--
-- Name: agenda_configuracionagenda_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.agenda_configuracionagenda_id_seq', 1, true);


--
-- Name: agenda_diabloqueado_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.agenda_diabloqueado_id_seq', 1, false);


--
-- Name: agenda_enviocorreo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.agenda_enviocorreo_id_seq', 1, false);


--
-- Name: agenda_visita_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.agenda_visita_id_seq', 1, true);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 56, true);


--
-- Name: clientes_aprobacionmayorista_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.clientes_aprobacionmayorista_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 14, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 26, true);


--
-- Name: tiendas_solicituddeacceso_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tiendas_solicituddeacceso_id_seq', 2, true);


--
-- Name: tiendas_tienda_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tiendas_tienda_id_seq', 1, true);


--
-- Name: usuarios_usuario_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuarios_usuario_groups_id_seq', 1, false);


--
-- Name: usuarios_usuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuarios_usuario_id_seq', 2, true);


--
-- Name: usuarios_usuario_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuarios_usuario_user_permissions_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

\unrestrict AsCCqwGE4Rl6xDjgjoFKCHgb6H6X06TPW4JiJKcPSd7s8gCEA1eRqem5QNKqvQp

