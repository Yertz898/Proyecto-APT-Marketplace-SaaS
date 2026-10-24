--
-- PostgreSQL database dump
--

\restrict ISVtMBwabk2Grb5sgbhM3sk2KxzvVvwf0HKUgYluvwAfb6mo5he06wjCNbVB0bT

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

INSERT INTO public.tiendas_tienda (id, slug, nombre, activa, fecha_creacion, banner, color_acento, color_destacado, color_primario, color_primario_hover, instagram, logo, whatsapp, plan, tipografia) VALUES (1, 'joyas-ye', 'Joyas Ye', true, '2026-09-27 04:09:50.774017+00', '', '#C8A96A', '#E0A526', '#7C3AED', '#6D28D9', '', '', '', 'ultimate', 'inter');
INSERT INTO public.tiendas_tienda (id, slug, nombre, activa, fecha_creacion, banner, color_acento, color_destacado, color_primario, color_primario_hover, instagram, logo, whatsapp, plan, tipografia) VALUES (2, 'bazar-austral', 'Bazar Austral', true, '2026-10-04 23:29:16.582839+00', '', '#4A5568', '#D97706', '#0F766E', '#115E59', '', '', '', 'premium', 'inter');


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

INSERT INTO public.agenda_configuracionagenda (id, fecha_creacion, fecha_edicion, duracion_minutos, visitas_por_bloque, anticipacion_minima_horas, ventana_maxima_dias, confirmacion_automatica, direccion, indicaciones, correo_notificaciones, token_feed, tienda_id) VALUES (1, '2026-09-27 04:33:39.633656+00', '2026-09-27 04:33:39.633676+00', 30, 1, 24, 30, false, '', '', '','REEMPLAZAR-AL-RESTAURAR-token-de-ejemplo', 1);


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
INSERT INTO public.django_content_type (id, app_label, model) VALUES (15, 'catalogo', 'categoria');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (16, 'catalogo', 'lineagranel');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (17, 'catalogo', 'lote');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (18, 'catalogo', 'composicionlote');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (19, 'precios', 'tramoprecio');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (20, 'catalogo', 'producto');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (21, 'ingesta', 'carga');


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
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (57, 'Can add categoría', 15, 'add_categoria');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (58, 'Can change categoría', 15, 'change_categoria');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (59, 'Can delete categoría', 15, 'delete_categoria');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (60, 'Can view categoría', 15, 'view_categoria');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (61, 'Can add línea de granel', 16, 'add_lineagranel');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (62, 'Can change línea de granel', 16, 'change_lineagranel');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (63, 'Can delete línea de granel', 16, 'delete_lineagranel');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (64, 'Can view línea de granel', 16, 'view_lineagranel');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (65, 'Can add lote', 17, 'add_lote');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (66, 'Can change lote', 17, 'change_lote');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (67, 'Can delete lote', 17, 'delete_lote');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (68, 'Can view lote', 17, 'view_lote');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (69, 'Can add composición del lote', 18, 'add_composicionlote');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (70, 'Can change composición del lote', 18, 'change_composicionlote');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (71, 'Can delete composición del lote', 18, 'delete_composicionlote');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (72, 'Can view composición del lote', 18, 'view_composicionlote');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (73, 'Can add tramo de precio', 19, 'add_tramoprecio');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (74, 'Can change tramo de precio', 19, 'change_tramoprecio');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (75, 'Can delete tramo de precio', 19, 'delete_tramoprecio');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (76, 'Can view tramo de precio', 19, 'view_tramoprecio');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (77, 'Can add producto', 20, 'add_producto');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (78, 'Can change producto', 20, 'change_producto');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (79, 'Can delete producto', 20, 'delete_producto');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (80, 'Can view producto', 20, 'view_producto');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (81, 'Can add carga', 21, 'add_carga');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (82, 'Can change carga', 21, 'change_carga');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (83, 'Can delete carga', 21, 'delete_carga');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (84, 'Can view carga', 21, 'view_carga');


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: catalogo_categoria; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.catalogo_categoria (id, fecha_creacion, fecha_edicion, nombre, tienda_id) VALUES (8, '2026-10-04 23:29:16.448151+00', '2026-10-04 23:29:16.44817+00', 'anillos', 1);
INSERT INTO public.catalogo_categoria (id, fecha_creacion, fecha_edicion, nombre, tienda_id) VALUES (9, '2026-10-04 23:29:16.450706+00', '2026-10-04 23:29:16.450715+00', 'aros', 1);
INSERT INTO public.catalogo_categoria (id, fecha_creacion, fecha_edicion, nombre, tienda_id) VALUES (10, '2026-10-04 23:29:16.4525+00', '2026-10-04 23:29:16.452508+00', 'cadenas', 1);
INSERT INTO public.catalogo_categoria (id, fecha_creacion, fecha_edicion, nombre, tienda_id) VALUES (11, '2026-10-04 23:29:16.45496+00', '2026-10-04 23:29:16.454972+00', 'collares', 1);
INSERT INTO public.catalogo_categoria (id, fecha_creacion, fecha_edicion, nombre, tienda_id) VALUES (12, '2026-10-04 23:29:16.45727+00', '2026-10-04 23:29:16.457282+00', 'colgantes', 1);
INSERT INTO public.catalogo_categoria (id, fecha_creacion, fecha_edicion, nombre, tienda_id) VALUES (13, '2026-10-04 23:29:16.459096+00', '2026-10-04 23:29:16.459106+00', 'pulseras', 1);
INSERT INTO public.catalogo_categoria (id, fecha_creacion, fecha_edicion, nombre, tienda_id) VALUES (14, '2026-10-04 23:29:16.460877+00', '2026-10-04 23:29:16.460885+00', 'tobilleras', 1);
INSERT INTO public.catalogo_categoria (id, fecha_creacion, fecha_edicion, nombre, tienda_id) VALUES (15, '2026-10-04 23:29:16.587623+00', '2026-10-04 23:29:16.587646+00', 'cocina', 2);
INSERT INTO public.catalogo_categoria (id, fecha_creacion, fecha_edicion, nombre, tienda_id) VALUES (16, '2026-10-04 23:29:16.589998+00', '2026-10-04 23:29:16.590008+00', 'escritorio', 2);
INSERT INTO public.catalogo_categoria (id, fecha_creacion, fecha_edicion, nombre, tienda_id) VALUES (17, '2026-10-04 23:29:16.591875+00', '2026-10-04 23:29:16.591887+00', 'hogar', 2);


--
-- Data for Name: catalogo_producto; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (25, '2026-10-13 00:31:34.060565+00', '2026-10-13 00:31:34.060576+00', 'EJEMPLO-01', 'Nombre del producto', 'Descripción breve', 4990, '', true, 'unidad', 'unidad', true, 10.000, 1.000, NULL, NULL, 1);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (7, '2026-10-04 23:29:16.465395+00', '2026-10-12 23:37:27.890412+00', 'granel-hombre', 'Gramo de hombre (cadenas y pulseras)', 'Enchape de plata · cadenas y pulseras.', 650, '', true, 'peso', 'g', false, NULL, 1.000, NULL, NULL, 1);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (8, '2026-10-04 23:29:16.482871+00', '2026-10-12 23:37:27.911378+00', 'granel-mujer', 'Gramo de mujer (cadenas, collares, pulseras y tobilleras)', 'Enchape de plata · cadenas, collares, pulseras y tobilleras.', 900, '', true, 'peso', 'g', false, NULL, 1.000, NULL, NULL, 1);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (9, '2026-10-04 23:29:16.496554+00', '2026-10-12 23:37:27.923225+00', 'granel-colgantes-aros-anillos', 'Gramo de colgantes, aros y anillos', 'Enchape de plata · colgantes, aros y anillos.', 1500, '', true, 'peso', 'g', false, NULL, 1.000, NULL, NULL, 1);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (10, '2026-10-04 23:29:16.510804+00', '2026-10-12 23:37:27.934204+00', 'granel-plata-colombiana', 'Gramo de plata colombiana', 'Plata colombiana.', 1800, '', true, 'peso', 'g', false, NULL, 1.000, NULL, NULL, 1);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (11, '2026-10-04 23:29:16.515992+00', '2026-10-12 23:37:27.938708+00', 'granel-colgantes-hombre-xl', 'Gramo de colgantes de hombre XL', 'Enchape de plata · colgantes.', 1000, '', true, 'peso', 'g', false, NULL, 1.000, NULL, NULL, 1);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (12, '2026-10-04 23:29:16.523046+00', '2026-10-04 23:29:16.523058+00', 'DEMO-01', 'Surtido de aros (ejemplo)', 'Enchape de plata.', 45990, '', true, 'lote', 'unidad', true, 8.000, 1.000, 18, NULL, 1);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (13, '2026-10-04 23:29:16.532929+00', '2026-10-04 23:29:16.532941+00', 'DEMO-02', 'Mix de cadenas de hombre (ejemplo)', 'Enchape de plata.', 89990, '', true, 'lote', 'unidad', true, 5.000, 1.000, 15, NULL, 1);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (14, '2026-10-04 23:29:16.540984+00', '2026-10-04 23:29:16.540993+00', 'DEMO-03', 'Colección de colgantes (ejemplo)', 'Enchape de plata.', 62990, '', true, 'lote', 'unidad', true, 6.000, 1.000, 18, NULL, 1);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (15, '2026-10-04 23:29:16.548047+00', '2026-10-08 01:11:40.567183+00', 'DEMO-04', 'Pieza única de plata colombiana (ejemplo)', 'Plata colombiana. Se vende una sola vez.', 129990, '', true, 'lote', 'unidad', true, 1.000, 1.000, 1, NULL, 1);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (16, '2026-10-04 23:29:16.552453+00', '2026-10-04 23:29:16.552461+00', 'DEMO-05', 'Set de tobilleras y pulseras (ejemplo)', 'Enchape de plata.', 38990, '', true, 'lote', 'unidad', true, 10.000, 1.000, 16, NULL, 1);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (17, '2026-10-04 23:29:16.559904+00', '2026-10-04 23:29:16.559912+00', 'DEMO-06', 'Lote mixto de temporada (ejemplo)', 'Enchape de plata. Se vende una sola vez.', 74990, '', true, 'lote', 'unidad', true, 1.000, 1.000, 15, NULL, 1);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (18, '2026-10-04 23:29:16.594487+00', '2026-10-04 23:29:16.594499+00', 'BAZ-01', 'Taza de cerámica (ejemplo)', 'Cerámica esmaltada, 350 ml.', 4990, '', true, 'unidad', 'unidad', true, 120.000, 1.000, NULL, 15, 2);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (19, '2026-10-04 23:29:16.602156+00', '2026-10-04 23:29:16.602164+00', 'BAZ-02', 'Set de velas aromáticas (ejemplo)', 'Tres velas de cera de soya.', 7990, '', true, 'unidad', 'unidad', true, 60.000, 1.000, NULL, 17, 2);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (20, '2026-10-04 23:29:16.610082+00', '2026-10-04 23:29:16.610093+00', 'BAZ-03', 'Cuaderno de tapa dura (ejemplo)', '120 hojas, tamaño carta.', 5490, '', true, 'unidad', 'unidad', true, 200.000, 1.000, NULL, 16, 2);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (21, '2026-10-04 23:29:16.61449+00', '2026-10-04 23:29:16.614498+00', 'BAZ-04', 'Organizador de escritorio (ejemplo)', 'Madera de pino, cuatro compartimentos.', 12990, '', true, 'unidad', 'unidad', true, 18.000, 1.000, NULL, 16, 2);
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id) VALUES (22, '2026-10-04 23:29:16.616256+00', '2026-10-04 23:29:16.616264+00', 'BAZ-05', 'Tabla de picar de madera (ejemplo)', 'Lenga, 30 × 20 cm. Queda una.', 15990, '', true, 'unidad', 'unidad', true, 1.000, 1.000, NULL, 15, 2);


--
-- Data for Name: catalogo_composicionlote; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.catalogo_composicionlote (id, fecha_creacion, fecha_edicion, cantidad, categoria_id, tienda_id, producto_id) VALUES (1, '2026-10-04 23:29:16.526862+00', '2026-10-12 23:37:27.950507+00', 12, 9, 1, 12);
INSERT INTO public.catalogo_composicionlote (id, fecha_creacion, fecha_edicion, cantidad, categoria_id, tienda_id, producto_id) VALUES (2, '2026-10-04 23:29:16.530399+00', '2026-10-12 23:37:27.953051+00', 6, 8, 1, 12);
INSERT INTO public.catalogo_composicionlote (id, fecha_creacion, fecha_edicion, cantidad, categoria_id, tienda_id, producto_id) VALUES (3, '2026-10-04 23:29:16.535443+00', '2026-10-12 23:37:27.957021+00', 10, 10, 1, 13);
INSERT INTO public.catalogo_composicionlote (id, fecha_creacion, fecha_edicion, cantidad, categoria_id, tienda_id, producto_id) VALUES (4, '2026-10-04 23:29:16.538635+00', '2026-10-12 23:37:27.959135+00', 5, 13, 1, 13);
INSERT INTO public.catalogo_composicionlote (id, fecha_creacion, fecha_edicion, cantidad, categoria_id, tienda_id, producto_id) VALUES (5, '2026-10-04 23:29:16.54311+00', '2026-10-12 23:37:27.963429+00', 14, 12, 1, 14);
INSERT INTO public.catalogo_composicionlote (id, fecha_creacion, fecha_edicion, cantidad, categoria_id, tienda_id, producto_id) VALUES (6, '2026-10-04 23:29:16.545593+00', '2026-10-12 23:37:27.965398+00', 4, 10, 1, 14);
INSERT INTO public.catalogo_composicionlote (id, fecha_creacion, fecha_edicion, cantidad, categoria_id, tienda_id, producto_id) VALUES (7, '2026-10-04 23:29:16.550288+00', '2026-10-12 23:37:27.970105+00', 1, 11, 1, 15);
INSERT INTO public.catalogo_composicionlote (id, fecha_creacion, fecha_edicion, cantidad, categoria_id, tienda_id, producto_id) VALUES (8, '2026-10-04 23:29:16.555158+00', '2026-10-12 23:37:27.974043+00', 8, 14, 1, 16);
INSERT INTO public.catalogo_composicionlote (id, fecha_creacion, fecha_edicion, cantidad, categoria_id, tienda_id, producto_id) VALUES (9, '2026-10-04 23:29:16.557831+00', '2026-10-12 23:37:27.976321+00', 8, 13, 1, 16);
INSERT INTO public.catalogo_composicionlote (id, fecha_creacion, fecha_edicion, cantidad, categoria_id, tienda_id, producto_id) VALUES (10, '2026-10-04 23:29:16.562061+00', '2026-10-12 23:37:27.980219+00', 5, 8, 1, 17);
INSERT INTO public.catalogo_composicionlote (id, fecha_creacion, fecha_edicion, cantidad, categoria_id, tienda_id, producto_id) VALUES (11, '2026-10-04 23:29:16.564635+00', '2026-10-12 23:37:27.982235+00', 5, 9, 1, 17);
INSERT INTO public.catalogo_composicionlote (id, fecha_creacion, fecha_edicion, cantidad, categoria_id, tienda_id, producto_id) VALUES (12, '2026-10-04 23:29:16.567553+00', '2026-10-12 23:37:27.984147+00', 3, 11, 1, 17);
INSERT INTO public.catalogo_composicionlote (id, fecha_creacion, fecha_edicion, cantidad, categoria_id, tienda_id, producto_id) VALUES (13, '2026-10-04 23:29:16.569995+00', '2026-10-12 23:37:27.986529+00', 2, 10, 1, 17);


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
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (31, 'tiendas', '0004_agrega_plan_y_tipografia', '2026-10-04 19:17:29.700435+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (32, 'catalogo', '0001_initial', '2026-10-04 23:27:23.030378+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (33, 'precios', '0001_initial', '2026-10-04 23:27:23.065058+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (34, 'ingesta', '0001_initial', '2026-10-08 01:46:53.744833+00');


--
-- Data for Name: precios_tramoprecio; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (15, '2026-10-04 23:29:16.472091+00', '2026-10-12 23:37:27.900673+00', 'monto', 20000.00, 650, 7, 1);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (16, '2026-10-04 23:29:16.475117+00', '2026-10-12 23:37:27.904254+00', 'monto', 100000.00, 600, 7, 1);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (17, '2026-10-04 23:29:16.477812+00', '2026-10-12 23:37:27.906797+00', 'peso', 500.00, 560, 7, 1);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (18, '2026-10-04 23:29:16.480437+00', '2026-10-12 23:37:27.909016+00', 'peso', 1000.00, 500, 7, 1);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (19, '2026-10-04 23:29:16.48577+00', '2026-10-12 23:37:27.913955+00', 'monto', 20000.00, 900, 8, 1);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (20, '2026-10-04 23:29:16.48895+00', '2026-10-12 23:37:27.91654+00', 'monto', 100000.00, 850, 8, 1);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (21, '2026-10-04 23:29:16.491576+00', '2026-10-12 23:37:27.91863+00', 'peso', 500.00, 780, 8, 1);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (22, '2026-10-04 23:29:16.494042+00', '2026-10-12 23:37:27.921037+00', 'peso', 1000.00, 700, 8, 1);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (23, '2026-10-04 23:29:16.499434+00', '2026-10-12 23:37:27.925535+00', 'monto', 20000.00, 1500, 9, 1);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (24, '2026-10-04 23:29:16.502287+00', '2026-10-12 23:37:27.927725+00', 'monto', 100000.00, 1300, 9, 1);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (25, '2026-10-04 23:29:16.505519+00', '2026-10-12 23:37:27.930023+00', 'peso', 500.00, 1200, 9, 1);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (26, '2026-10-04 23:29:16.508293+00', '2026-10-12 23:37:27.932168+00', 'peso', 1000.00, 1050, 9, 1);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (27, '2026-10-04 23:29:16.513489+00', '2026-10-12 23:37:27.936494+00', 'monto', 20000.00, 1800, 10, 1);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (28, '2026-10-04 23:29:16.518983+00', '2026-10-12 23:37:27.941026+00', 'monto', 20000.00, 1000, 11, 1);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (29, '2026-10-04 23:29:16.597403+00', '2026-10-12 23:37:27.99853+00', 'cantidad', 12.00, 4490, 18, 2);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (30, '2026-10-04 23:29:16.600041+00', '2026-10-12 23:37:28.000673+00', 'cantidad', 48.00, 3990, 18, 2);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (31, '2026-10-04 23:29:16.604928+00', '2026-10-12 23:37:28.00555+00', 'cantidad', 6.00, 7290, 19, 2);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (32, '2026-10-04 23:29:16.607794+00', '2026-10-12 23:37:28.007716+00', 'cantidad', 24.00, 6590, 19, 2);
INSERT INTO public.precios_tramoprecio (id, fecha_creacion, fecha_edicion, unidad_umbral, umbral, valor, producto_id, tienda_id) VALUES (33, '2026-10-04 23:29:16.612391+00', '2026-10-12 23:37:28.011671+00', 'cantidad', 10.00, 4990, 20, 2);


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

SELECT pg_catalog.setval('public.auth_permission_id_seq', 84, true);


--
-- Name: catalogo_categoria_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.catalogo_categoria_id_seq', 17, true);


--
-- Name: catalogo_composicionlote_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.catalogo_composicionlote_id_seq', 13, true);


--
-- Name: catalogo_producto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.catalogo_producto_id_seq', 25, true);


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

SELECT pg_catalog.setval('public.django_content_type_id_seq', 21, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 34, true);


--
-- Name: precios_tramoprecio_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.precios_tramoprecio_id_seq', 33, true);


--
-- Name: tiendas_solicituddeacceso_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tiendas_solicituddeacceso_id_seq', 2, true);


--
-- Name: tiendas_tienda_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tiendas_tienda_id_seq', 2, true);


--
-- Name: usuarios_usuario_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuarios_usuario_groups_id_seq', 1, false);


--
-- Name: usuarios_usuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuarios_usuario_id_seq', 5, true);


--
-- Name: usuarios_usuario_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuarios_usuario_user_permissions_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

\unrestrict ISVtMBwabk2Grb5sgbhM3sk2KxzvVvwf0HKUgYluvwAfb6mo5he06wjCNbVB0bT

