--
-- PostgreSQL database dump
--

\restrict 261gl2mIEOo7hZW2xk9n17utZA538oOn85vzPS8edcPVRDS9KEMRXrsbUdPns4g

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

INSERT INTO public.agenda_configuracionagenda (id, fecha_creacion, fecha_edicion, duracion_minutos, visitas_por_bloque, anticipacion_minima_horas, ventana_maxima_dias, confirmacion_automatica, direccion, indicaciones, correo_notificaciones, token_feed, tienda_id) VALUES (1, '2026-09-27 04:33:39.633656+00', '2026-09-27 04:33:39.633676+00', 30, 1, 24, 30, false, '', '', '', 'RELLENO-REGENERAR-AL-RESTAURAR', 1);


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
INSERT INTO public.django_content_type (id, app_label, model) VALUES (22, 'pedidos', 'pedido');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (23, 'pedidos', 'lineapedido');


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
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (85, 'Can add Pedido', 22, 'add_pedido');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (86, 'Can change Pedido', 22, 'change_pedido');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (87, 'Can delete Pedido', 22, 'delete_pedido');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (88, 'Can view Pedido', 22, 'view_pedido');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (89, 'Can add Línea de pedido', 23, 'add_lineapedido');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (90, 'Can change Línea de pedido', 23, 'change_lineapedido');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (91, 'Can delete Línea de pedido', 23, 'delete_lineapedido');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (92, 'Can view Línea de pedido', 23, 'view_lineapedido');


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
INSERT INTO public.catalogo_categoria (id, fecha_creacion, fecha_edicion, nombre, tienda_id) VALUES (18, '2026-11-07 21:43:56.514663+00', '2026-11-07 21:43:56.514681+00', 'conjuntos', 1);


--
-- Data for Name: catalogo_producto; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (10, '2026-11-10 20:02:05.086127+00', '2026-10-12 23:37:27.934204+00', 'granel-plata-colombiana', 'Gramo de plata colombiana', 'Plata colombiana.', 1800, '', true, 'peso', 'g', false, NULL, 1.000, NULL, NULL, 1, '');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (33, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.022217+00', 'LOTE-122', 'Lote 122 de conjuntos', '', 21849, 'productos/LOTE-122_wVQO2jp.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-122-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (34, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.035635+00', 'LOTE-056', 'Lote 56 de anillos', '', 17647, 'productos/LOTE-056_MZraFYo.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 8, 1, 'lote-056-anillos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (35, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.04976+00', 'LOTE-138', 'Lote 138 de aros', '', 13445, 'productos/LOTE-138_z6oPrS8.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 9, 1, 'lote-138-aros.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (18, '2026-10-04 23:29:16.594487+00', '2026-10-04 23:29:16.594499+00', 'BAZ-01', 'Taza de cerámica (ejemplo)', 'Cerámica esmaltada, 350 ml.', 4990, '', true, 'unidad', 'unidad', true, 120.000, 1.000, NULL, 15, 2, '');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (19, '2026-10-04 23:29:16.602156+00', '2026-10-04 23:29:16.602164+00', 'BAZ-02', 'Set de velas aromáticas (ejemplo)', 'Tres velas de cera de soya.', 7990, '', true, 'unidad', 'unidad', true, 60.000, 1.000, NULL, 17, 2, '');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (20, '2026-10-04 23:29:16.610082+00', '2026-10-04 23:29:16.610093+00', 'BAZ-03', 'Cuaderno de tapa dura (ejemplo)', '120 hojas, tamaño carta.', 5490, '', true, 'unidad', 'unidad', true, 200.000, 1.000, NULL, 16, 2, '');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (21, '2026-10-04 23:29:16.61449+00', '2026-10-04 23:29:16.614498+00', 'BAZ-04', 'Organizador de escritorio (ejemplo)', 'Madera de pino, cuatro compartimentos.', 12990, '', true, 'unidad', 'unidad', true, 18.000, 1.000, NULL, 16, 2, '');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (22, '2026-10-04 23:29:16.616256+00', '2026-10-04 23:29:16.616264+00', 'BAZ-05', 'Tabla de picar de madera (ejemplo)', 'Lenga, 30 × 20 cm. Queda una.', 15990, '', true, 'unidad', 'unidad', true, 1.000, 1.000, NULL, 15, 2, '');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (36, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.062833+00', 'LOTE-141', 'Lote 141 de pulseras', '', 21008, 'productos/LOTE-141_BQeEfLQ.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-141-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (37, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.077384+00', 'LOTE-143', 'Lote 143 de pulseras', '', 17647, 'productos/LOTE-143_YxJw8eE.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-143-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (38, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.090844+00', 'LOTE-129', 'Lote 129 de pulseras', '', 33613, 'productos/LOTE-129_AbYEbNi.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-129-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (39, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.10455+00', 'LOTE-153', 'Lote 153 de anillos', '', 14286, 'productos/LOTE-153_t09fNhf.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 8, 1, 'lote-153-anillos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (40, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.118781+00', 'LOTE-144', 'Lote 144 de pulseras', '', 26891, 'productos/LOTE-144_1biGhRp.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-144-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (41, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.133225+00', 'LOTE-173', 'Lote 173 de collares', '', 15126, 'productos/LOTE-173_K4Uix4B.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 11, 1, 'lote-173-collares.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (42, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.148003+00', 'LOTE-180', 'Lote 180 de conjuntos', '', 18487, 'productos/LOTE-180_AyJKqQY.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-180-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (43, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.162046+00', 'LOTE-163', 'Lote 163 de pulseras', '', 14286, 'productos/LOTE-163_c6R7nrJ.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-163-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (44, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.177094+00', 'LOTE-170', 'Lote 170 de pulseras', '', 16807, 'productos/LOTE-170_RJI7jna.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-170-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (45, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.192313+00', 'LOTE-168', 'Lote 168 de anillos', '', 21849, 'productos/LOTE-168_DOjdbOl.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 8, 1, 'lote-168-anillos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (46, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.205214+00', 'LOTE-194', 'Lote 194 de anillos', '', 13025, 'productos/LOTE-194_nwtwlQp.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 8, 1, 'lote-194-anillos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (47, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.219829+00', 'LOTE-186', 'Lote 186 de anillos', '', 19328, 'productos/LOTE-186_LeDsCBP.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 8, 1, 'lote-186-anillos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (48, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.235428+00', 'LOTE-198', 'Lote 198 de aros', '', 21849, 'productos/LOTE-198_HCTRXTz.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 9, 1, 'lote-198-aros.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (49, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.249832+00', 'LOTE-199', 'Lote 199 de aros', '', 21428, 'productos/LOTE-199_0A6zKfj.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 9, 1, 'lote-199-aros.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (50, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.265628+00', 'LOTE-197', 'Lote 197 de aros', '', 22269, 'productos/LOTE-197_c0yYsYQ.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 9, 1, 'lote-197-aros.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (51, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.280764+00', 'LOTE-202', 'Lote 202 de aros', '', 17647, 'productos/LOTE-202_K8jwG6t.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 9, 1, 'lote-202-aros.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (88, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.802661+00', 'LOTE-251', 'Lote 251 de pulseras', '', 16807, 'productos/LOTE-251_9faWIPc.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-251-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (89, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.816349+00', 'LOTE-256', 'Lote 256 de anillos', '', 18487, 'productos/LOTE-256_m4YciYd.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 8, 1, 'lote-256-anillos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (90, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.829058+00', 'LOTE-260', 'Lote 260 de anillos', '', 20168, 'productos/LOTE-260_C2GzOOI.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 8, 1, 'lote-260-anillos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (91, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.842897+00', 'LOTE-261', 'Lote 261 de anillos', '', 21008, 'productos/LOTE-261_ab4Co2B.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 8, 1, 'lote-261-anillos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (92, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.855339+00', 'LOTE-262', 'Lote 262 de anillos', '', 13445, 'productos/LOTE-262_TGfWRJ3.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 8, 1, 'lote-262-anillos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (93, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.868473+00', 'LOTE-263', 'Lote 263 de anillos', '', 16807, 'productos/LOTE-263_EtU2lJO.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 8, 1, 'lote-263-anillos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (94, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.881532+00', 'LOTE-259', 'Lote 259 de anillos', '', 17647, 'productos/LOTE-259_UWIJkc5.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 8, 1, 'lote-259-anillos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (95, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.894807+00', 'LOTE-265', 'Lote 265 de anillos', '', 15546, 'productos/LOTE-265_ChQlGAu.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 8, 1, 'lote-265-anillos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (96, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.908424+00', 'LOTE-267', 'Lote 267 de colgantes', '', 12605, 'productos/LOTE-267_O7IdpR9.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 12, 1, 'lote-267-colgantes.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (97, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.922741+00', 'LOTE-268', 'Lote 268 de colgantes', '', 12605, 'productos/LOTE-268_70aEq2L.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 12, 1, 'lote-268-colgantes.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (98, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.936562+00', 'LOTE-269', 'Lote 269 de colgantes', '', 12605, 'productos/LOTE-269_yukZAq7.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 12, 1, 'lote-269-colgantes.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (99, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.951441+00', 'LOTE-270', 'Lote 270 de colgantes', '', 12605, 'productos/LOTE-270_uN0YFev.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 12, 1, 'lote-270-colgantes.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (100, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.967218+00', 'LOTE-264', 'Lote 264 de anillos', '', 14286, 'productos/LOTE-264_mIjdpKa.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 8, 1, 'lote-264-anillos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (101, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.981773+00', 'LOTE-272', 'Lote 272 de conjuntos', '', 15126, 'productos/LOTE-272_gvb2cSm.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-272-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (102, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.996699+00', 'LOTE-273', 'Lote 273 de conjuntos', '', 16807, 'productos/LOTE-273_MoNl4Bu.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-273-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (52, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.294922+00', 'LOTE-205', 'Lote 205 de conjuntos', '', 14286, 'productos/LOTE-205_UNDhD7e.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-205-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (53, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.311092+00', 'LOTE-206', 'Lote 206 de conjuntos', '', 15966, 'productos/LOTE-206_6O0OXtL.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-206-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (54, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.325839+00', 'LOTE-207', 'Lote 207 de conjuntos', '', 19748, 'productos/LOTE-207_hbo0Qp2.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-207-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (55, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.340906+00', 'LOTE-200', 'Lote 200 de aros', '', 18487, 'productos/LOTE-200_KpX2c2L.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 9, 1, 'lote-200-aros.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (56, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.356+00', 'LOTE-210', 'Lote 210 de conjuntos', '', 19748, 'productos/LOTE-210_9ABjfLg.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-210-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (57, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.371459+00', 'LOTE-211', 'Lote 211 de colibries', '', 17227, 'productos/LOTE-211_VrLMZng.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 12, 1, 'lote-211-colibries.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (58, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.387054+00', 'LOTE-212', 'Lote 212 de nudo de bruja', '', 20168, 'productos/LOTE-212_y7wTH8Y.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 12, 1, 'lote-212-nudo-de-bruja.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (59, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.40228+00', 'LOTE-214', 'Lote 214 de aros', '', 14286, 'productos/LOTE-214_83yQ9LG.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 9, 1, 'lote-214-aros.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (60, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.417031+00', 'LOTE-215', 'Lote 215 de conjuntos', '', 14706, 'productos/LOTE-215_fDCMezK.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-215-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (61, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.432591+00', 'LOTE-209', 'Lote 209 de crucifijos', '', 31092, 'productos/LOTE-209_dYupabl.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 12, 1, 'lote-209-crucifijos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (62, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.445391+00', 'LOTE-224', 'Lote 224 de cadenas', '', 33613, 'productos/LOTE-224_S0L9JWJ.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 10, 1, 'lote-224-cadenas.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (63, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.458993+00', 'LOTE-225', 'Lote 225 de pulseras', '', 29412, 'productos/LOTE-225_n2v2dO7.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-225-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (64, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.472381+00', 'LOTE-226', 'Lote 226 de collares', '', 14286, 'productos/LOTE-226_ig9LuVh.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 11, 1, 'lote-226-collares.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (65, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.486019+00', 'LOTE-228', 'Lote 228 de pulseras', '', 12605, 'productos/LOTE-228_bqlLPKy.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-228-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (66, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.500395+00', 'LOTE-229', 'Lote 229 de pulseras', '', 15966, 'productos/LOTE-229_WWMnMNu.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-229-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (67, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.513532+00', 'LOTE-218', 'Lote 218 de pulseras', '', 27731, 'productos/LOTE-218_DtfYfBr.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-218-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (68, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.52681+00', 'LOTE-233', 'Lote 233 de pulseras', '', 15126, 'productos/LOTE-233_le661X0.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-233-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (69, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.540782+00', 'LOTE-234', 'Lote 234 de pulseras', '', 14286, 'productos/LOTE-234_soN2Cyp.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-234-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (70, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.554712+00', 'LOTE-235', 'Lote 235 de pulseras', '', 17647, 'productos/LOTE-235_YXQq332.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-235-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (71, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.568175+00', 'LOTE-236', 'Lote 236 de pulseras', '', 16807, 'productos/LOTE-236_UABm5nF.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-236-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (72, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.581938+00', 'LOTE-230', 'Lote 230 de pulseras', '', 16807, 'productos/LOTE-230_OZdKd8Z.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-230-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (73, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.59476+00', 'LOTE-242', 'Lote 242 de conjuntos', '', 16807, 'productos/LOTE-242_4rstojE.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-242-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (74, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.609864+00', 'LOTE-243', 'Lote 243 de cadenas de hombre', 'Lleva 8 cadenas y 4 colgantes.', 31092, 'productos/LOTE-243_XLmmjlI.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 10, 1, 'lote-243-cadenas-de-hombre.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (75, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.624122+00', 'LOTE-244', 'Lote 244 de cadenas', '', 33613, 'productos/LOTE-244_O7b6gc9.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 10, 1, 'lote-244-cadenas.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (76, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.63781+00', 'LOTE-245', 'Lote 245 de cadenas', '', 15966, 'productos/LOTE-245_8dL7C3n.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 10, 1, 'lote-245-cadenas.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (77, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.651257+00', 'LOTE-241', 'Lote 241 de conjuntos', '', 15966, 'productos/LOTE-241_4dDk20c.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-241-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (78, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.667458+00', 'LOTE-247', 'Lote 247 de tobilleras', '', 16807, 'productos/LOTE-247_VvEpZW6.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 14, 1, 'lote-247-tobilleras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (79, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.681266+00', 'LOTE-248', 'Lote 248 de tobilleras', '', 12605, 'productos/LOTE-248_GpQki53.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 14, 1, 'lote-248-tobilleras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (7, '2026-11-10 20:02:05.086127+00', '2026-10-12 23:37:27.890412+00', 'granel-hombre', 'Gramo de hombre (cadenas y pulseras)', 'Enchape de plata · cadenas y pulseras.', 650, '', true, 'peso', 'g', false, NULL, 1.000, NULL, NULL, 1, '');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (8, '2026-11-10 20:02:05.086127+00', '2026-10-12 23:37:27.911378+00', 'granel-mujer', 'Gramo de mujer (cadenas, collares, pulseras y tobilleras)', 'Enchape de plata · cadenas, collares, pulseras y tobilleras.', 900, '', true, 'peso', 'g', false, NULL, 1.000, NULL, NULL, 1, '');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (9, '2026-11-10 20:02:05.086127+00', '2026-10-12 23:37:27.923225+00', 'granel-colgantes-aros-anillos', 'Gramo de colgantes, aros y anillos', 'Enchape de plata · colgantes, aros y anillos.', 1500, '', true, 'peso', 'g', false, NULL, 1.000, NULL, NULL, 1, '');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (11, '2026-11-10 20:02:05.086127+00', '2026-10-12 23:37:27.938708+00', 'granel-colgantes-hombre-xl', 'Gramo de colgantes de hombre XL', 'Enchape de plata · colgantes.', 1000, '', true, 'peso', 'g', false, NULL, 1.000, NULL, NULL, 1, '');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (26, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:43.917351+00', 'LOTE-039', 'Lote 39 de pulseras', '', 15966, 'productos/LOTE-039_b5WszJ7.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-039-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (27, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:43.934991+00', 'LOTE-023', 'Lote 23 de pulseras', 'Lleva 10 pulseras.', 16807, 'productos/LOTE-023_Etlbt5o.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-023-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (28, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:43.949876+00', 'LOTE-048', 'Lote 48 de pulseras', '', 15126, 'productos/LOTE-048_u3yCJDS.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-048-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (29, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:43.964944+00', 'LOTE-052', 'Lote 52 de pulseras', 'Lleva 16 pulseras.', 25210, 'productos/LOTE-052_SZaCbad.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-052-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (30, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:43.978247+00', 'LOTE-045', 'Lote 45 de pulseras', '', 15966, 'productos/LOTE-045_r7vqzPd.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-045-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (31, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:43.994225+00', 'LOTE-119', 'Lote 119 de cadenas', '', 29412, 'productos/LOTE-119_RLHZ7ex.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 10, 1, 'lote-119-cadenas.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (32, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.008873+00', 'LOTE-120', 'Lote 120 de cadenas', '', 21008, 'productos/LOTE-120_50ZVQhH.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 10, 1, 'lote-120-cadenas.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (80, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.693567+00', 'LOTE-249', 'Lote 249 de tobilleras', '', 12605, 'productos/LOTE-249_WnshK32.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 14, 1, 'lote-249-tobilleras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (81, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.707919+00', 'LOTE-250', 'Lote 250 de pulseras', '', 14286, 'productos/LOTE-250_mI7btFD.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 13, 1, 'lote-250-pulseras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (82, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.721412+00', 'LOTE-246', 'Lote 246 de tobilleras', '', 15126, 'productos/LOTE-246_jQGqYqS.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 14, 1, 'lote-246-tobilleras.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (83, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.735976+00', 'LOTE-252', 'Lote 252 de aros', '', 16807, 'productos/LOTE-252_BfWmUq7.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 9, 1, 'lote-252-aros.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (84, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.749481+00', 'LOTE-253', 'Lote 253 de aros', '', 11765, 'productos/LOTE-253_TYgyOJs.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 9, 1, 'lote-253-aros.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (85, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.761923+00', 'LOTE-254', 'Lote 254 de aros', '', 10084, 'productos/LOTE-254_sJPfcAh.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 9, 1, 'lote-254-aros.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (86, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.775176+00', 'LOTE-255', 'Lote 255 de aros', '', 10084, 'productos/LOTE-255_bVQ2FOJ.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 9, 1, 'lote-255-aros.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (87, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:44.787252+00', 'LOTE-257', 'Lote 257 de aros', '', 13445, 'productos/LOTE-257_vY3q4RC.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 9, 1, 'lote-257-aros.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (103, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:45.01199+00', 'LOTE-274', 'Lote 274 de conjuntos', '', 14286, 'productos/LOTE-274_KVBjBtB.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-274-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (104, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:45.026932+00', 'LOTE-275', 'Lote 275 de conjuntos', '', 15546, 'productos/LOTE-275_hGDRHTP.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-275-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (105, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:45.041135+00', 'LOTE-271', 'Lote 271 de colgantes', '', 17647, 'productos/LOTE-271_d0RLfo9.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 12, 1, 'lote-271-colgantes.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (106, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:45.055161+00', 'LOTE-277', 'Lote 277 de conjuntos', '', 15126, 'productos/LOTE-277_SmrpTmC.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-277-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (107, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:45.070283+00', 'LOTE-278', 'Lote 278 de conjuntos', '', 14286, 'productos/LOTE-278_DRJ3FtB.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-278-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (108, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:45.084633+00', 'LOTE-276', 'Lote 276 de conjuntos', '', 13025, 'productos/LOTE-276_fQrqt7R.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 18, 1, 'lote-276-conjuntos.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (109, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:45.099695+00', 'LOTE-AROS-ENROSCADOS', 'Lote de aros enroscados', 'Lleva 9 pares de aros. Incluye exhibidor.', 46218, 'productos/LOTE-AROS-ENROSCADOS_tk0avcg.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 9, 1, 'lote-aros-enroscados.jpeg');
INSERT INTO public.catalogo_producto (id, fecha_creacion, fecha_edicion, codigo, nombre, descripcion, precio_neto, foto, activo, forma_venta, unidad_medida, controla_stock, stock, cantidad_minima, cantidad_piezas, categoria_id, tienda_id, archivo_de_la_foto) VALUES (110, '2026-11-10 20:02:05.086127+00', '2026-11-10 17:47:45.111527+00', 'LOTE-ANILLOS-MALETA', 'Lote de anillos', 'Lleva 10 anillos. Incluye maleta.', 42017, 'productos/LOTE-ANILLOS-MALETA_3selRDh.jpeg', true, 'lote', 'unidad', false, NULL, 1.000, NULL, 8, 1, 'lote-anillos-maleta.jpeg');


--
-- Data for Name: catalogo_composicionlote; Type: TABLE DATA; Schema: public; Owner: -
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
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (31, 'tiendas', '0004_agrega_plan_y_tipografia', '2026-10-04 19:17:29.700435+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (32, 'catalogo', '0001_initial', '2026-10-04 23:27:23.030378+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (33, 'precios', '0001_initial', '2026-10-04 23:27:23.065058+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (34, 'ingesta', '0001_initial', '2026-10-08 01:46:53.744833+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (35, 'pedidos', '0001_initial', '2026-11-08 00:02:26.918445+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (36, 'catalogo', '0002_producto_archivo_de_la_foto', '2026-11-10 17:38:00.188136+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (37, 'pedidos', '0002_alter_pedido_options_and_more', '2026-11-10 19:51:02.969422+00');


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

SELECT pg_catalog.setval('public.auth_permission_id_seq', 92, true);


--
-- Name: catalogo_categoria_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.catalogo_categoria_id_seq', 18, true);


--
-- Name: catalogo_composicionlote_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.catalogo_composicionlote_id_seq', 13, true);


--
-- Name: catalogo_producto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.catalogo_producto_id_seq', 110, true);


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

SELECT pg_catalog.setval('public.django_content_type_id_seq', 23, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 37, true);


--
-- Name: pedidos_lineapedido_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pedidos_lineapedido_id_seq', 9606, true);


--
-- Name: pedidos_pedido_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pedidos_pedido_id_seq', 5601, true);


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

\unrestrict 261gl2mIEOo7hZW2xk9n17utZA538oOn85vzPS8edcPVRDS9KEMRXrsbUdPns4g

