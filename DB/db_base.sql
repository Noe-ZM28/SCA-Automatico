-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 21-09-2023 a las 18:37:15
-- Versión del servidor: 10.4.22-MariaDB
-- Versión de PHP: 8.1.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `db_test`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Cortes`
--

CREATE TABLE `Cortes` (
  `Folio` bigint(20) UNSIGNED NOT NULL,
  `FechaIni` datetime NOT NULL,
  `FechaFin` datetime NOT NULL,
  `Importe` int(11) DEFAULT NULL,
  `NumBoletos` int(11) DEFAULT NULL,
  `TipoDCorte` smallint(6) DEFAULT NULL,
  `Quedados` int(11) DEFAULT NULL,
  `idInicial` int(11) DEFAULT NULL,
  `NumBolQued` int(11) DEFAULT NULL,
   `Pensionados_Quedados` INT(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `Cortes`
--

INSERT INTO `Cortes` (`Folio`, `FechaIni`, `FechaFin`, `Importe`, `NumBoletos`, `TipoDCorte`, `Quedados`, `idInicial`, `NumBolQued`) VALUES
(1, '2023-09-21 10:30:04', '2023-09-21 10:30:34', 0, NULL, NULL, 0, 1, 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Entradas`
--

CREATE TABLE `Entradas` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `Entrada` datetime NOT NULL,
  `Salida` datetime DEFAULT NULL,
  `TiempoTotal` varchar(255) DEFAULT NULL,
  `Importe` float DEFAULT NULL,
  `CorteInc` int(11) DEFAULT NULL,
  `vobo` varchar(5) DEFAULT NULL,
  `Placas` varchar(255) DEFAULT NULL,
  `TarifaPreferente` varchar(255) DEFAULT NULL,
  `TipoPromocion` varchar(255) DEFAULT NULL,
  `QRpromo` varchar(25) DEFAULT NULL,
  `Motivo` VARCHAR(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `Entradas`
--

INSERT INTO `Entradas` (`id`, `Entrada`, `Salida`, `TiempoTotal`, `Importe`, `CorteInc`, `vobo`, `Placas`, `TarifaPreferente`, `TipoPromocion`, `QRpromo`) VALUES
(1, '2023-09-21 02:02:02', '2023-09-21 10:30:21', '8:28:19', 0, 1, 'cor', 'XYZ123', 'CDO', NULL, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `MovimientosPens`
--

CREATE TABLE `MovimientosPens` (
  `Id_movs` int(10) UNSIGNED NOT NULL,
  `Idcliente` int(10) UNSIGNED NOT NULL,
  `num_tarjeta` int(11) NOT NULL,
  `Entrada` datetime DEFAULT NULL,
  `Salida` datetime DEFAULT NULL,
  `TiempoTotal` varchar(255) DEFAULT NULL,
  `Estatus` varchar(15) DEFAULT NULL,
  `Corte` INT(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `MovsUsuarios`
--

CREATE TABLE `MovsUsuarios` (
  `Id_movs` int(10) UNSIGNED NOT NULL,
  `Idusuario` int(10) UNSIGNED NOT NULL,
  `usuario` varchar(25) NOT NULL,
  `inicio` datetime DEFAULT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `turno` int(11) DEFAULT NULL,
  `comentarios` varchar(255) DEFAULT NULL,
  `CierreCorte` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `MovsUsuarios`
--

INSERT INTO `MovsUsuarios` (`Id_movs`, `Idusuario`, `usuario`, `inicio`, `nombre`, `turno`, `comentarios`, `CierreCorte`) VALUES
(1, 1, 'Admin', '2023-09-21 10:30:04', 'Administrador', 1, NULL, '2023-09-21 10:30:35.');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `PagosPens`
--

CREATE TABLE `PagosPens` (
  `Id_pago` int(10) UNSIGNED NOT NULL,
  `Idcliente` int(10) UNSIGNED NOT NULL,
  `num_tarjeta` int(11) NOT NULL,
  `Fecha_pago` datetime DEFAULT NULL,
  `Fecha_vigencia` datetime DEFAULT NULL,
  `Mensualidad` varchar(255) DEFAULT NULL,
  `Monto` float DEFAULT NULL,
  `TipoPago` enum('Transferencia','Efectivo') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Pensionados`
--

CREATE TABLE `Pensionados` (
  `Id_cliente` int(10) UNSIGNED NOT NULL,
  `Num_tarjeta` int(11) NOT NULL,
  `Nom_cliente` varchar(255) DEFAULT NULL,
  `Apell1_cliente` varchar(255) DEFAULT NULL,
  `Apell2_cliente` varchar(255) DEFAULT NULL,
  `Fecha_alta` datetime DEFAULT NULL,
  `Telefono1` varchar(25) DEFAULT NULL,
  `Telefono2` varchar(25) DEFAULT NULL,
  `Ciudad` varchar(255) DEFAULT NULL,
  `Colonia` varchar(255) DEFAULT NULL,
  `CP` varchar(8) DEFAULT NULL,
  `Calle_num` varchar(255) DEFAULT NULL,
  `Placas` varchar(50) DEFAULT NULL,
  `Modelo_auto` varchar(50) DEFAULT NULL,
  `Color_auto` varchar(20) DEFAULT NULL,
  `Vigencia` varchar(20) DEFAULT NULL,
  `Fecha_vigencia` datetime DEFAULT NULL,
  `Monto` int(15) DEFAULT NULL,
  `Estatus` varchar(20) DEFAULT NULL,
  `Tolerancia` varchar(20) DEFAULT NULL,
  `Cortesia` varchar(20) DEFAULT NULL,
  `Ult_Cambio` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Usuarios`
--

CREATE TABLE `Usuarios` (
  `Id_usuario` int(10) UNSIGNED NOT NULL,
  `Usuario` varchar(25) NOT NULL,
  `Contrasena` varchar(25) DEFAULT NULL,
  `Nom_usuario` varchar(255) DEFAULT NULL,
  `Fecha_alta` datetime DEFAULT NULL,
  `Telefono1` varchar(25) DEFAULT NULL,
  `Aviso_Emer` varchar(255) DEFAULT NULL,
  `TelefonoEmer` varchar(25) DEFAULT NULL,
  `Sucursal` varchar(25) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla `Usuarios`
--

INSERT INTO `Usuarios` (`Id_usuario`, `Usuario`, `Contrasena`, `Nom_usuario`, `Fecha_alta`, `Telefono1`, `Aviso_Emer`, `TelefonoEmer`, `Sucursal`) VALUES
(1, 'Admin', 'PASE', 'Administrador', NULL, NULL, NULL, NULL, NULL);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `Cortes`
--
ALTER TABLE `Cortes`
  ADD PRIMARY KEY (`Folio`);

--
-- Indices de la tabla `Entradas`
--
ALTER TABLE `Entradas`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `MovimientosPens`
--
ALTER TABLE `MovimientosPens`
  ADD PRIMARY KEY (`Id_movs`),
  ADD KEY `Idcliente` (`Idcliente`);

--
-- Indices de la tabla `MovsUsuarios`
--
ALTER TABLE `MovsUsuarios`
  ADD PRIMARY KEY (`Id_movs`),
  ADD KEY `Idusuario` (`Idusuario`);

--
-- Indices de la tabla `PagosPens`
--
ALTER TABLE `PagosPens`
  ADD PRIMARY KEY (`Id_pago`),
  ADD KEY `Idcliente` (`Idcliente`);

--
-- Indices de la tabla `Pensionados`
--
ALTER TABLE `Pensionados`
  ADD PRIMARY KEY (`Id_cliente`);

--
-- Indices de la tabla `Usuarios`
--
ALTER TABLE `Usuarios`
  ADD PRIMARY KEY (`Id_usuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `Cortes`
--
ALTER TABLE `Cortes`
  MODIFY `Folio` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT de la tabla `Entradas`
--
ALTER TABLE `Entradas`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT de la tabla `MovimientosPens`
--
ALTER TABLE `MovimientosPens`
  MODIFY `Id_movs` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `MovsUsuarios`
--
ALTER TABLE `MovsUsuarios`
  MODIFY `Id_movs` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- AUTO_INCREMENT de la tabla `PagosPens`
--
ALTER TABLE `PagosPens`
  MODIFY `Id_pago` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Pensionados`
--
ALTER TABLE `Pensionados`
  MODIFY `Id_cliente` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Usuarios`
--
ALTER TABLE `Usuarios`
  MODIFY `Id_usuario` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `MovimientosPens`
--
ALTER TABLE `MovimientosPens`
  ADD CONSTRAINT `MovimientosPens_ibfk_1` FOREIGN KEY (`Idcliente`) REFERENCES `Pensionados` (`Id_cliente`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `MovsUsuarios`
--
ALTER TABLE `MovsUsuarios`
  ADD CONSTRAINT `MovsUsuarios_ibfk_1` FOREIGN KEY (`Idusuario`) REFERENCES `Usuarios` (`Id_usuario`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `PagosPens`
--
ALTER TABLE `PagosPens`
  ADD CONSTRAINT `PagosPens_ibfk_1` FOREIGN KEY (`Idcliente`) REFERENCES `Pensionados` (`Id_cliente`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
