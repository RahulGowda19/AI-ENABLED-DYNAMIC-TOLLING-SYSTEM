-- phpMyAdmin SQL Dump
-- version 4.5.1
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Mar 22, 2025 at 07:27 AM
-- Server version: 10.1.16-MariaDB
-- PHP Version: 7.0.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `number_plate`
--

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `address` text NOT NULL,
  `mobile_no` varchar(15) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `address`, `mobile_no`, `password`) VALUES
(2, 'joseph', 'Mangalore', '9740319908', '$2b$12$fV/em65XnWjaNQS7xWOSmuNObZ9Ghu0h.0Oaa1mJwIZ3e70T.ngn6'),
(3, 'jobin', 'Mangalore', '9740319908', '$2b$12$RuT4hwimDrlktfg926dfc.F4wuAuE4Uo23JYDUDhgZCc1NPdIOz8y');

-- --------------------------------------------------------

--
-- Table structure for table `vehicle_registration`
--

CREATE TABLE `vehicle_registration` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `address` text NOT NULL,
  `vehicle_number` varchar(20) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `status` enum('Paid','Pending') NOT NULL DEFAULT 'Paid',
  `registered_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `vehicle_registration`
--

INSERT INTO `vehicle_registration` (`id`, `name`, `address`, `vehicle_number`, `amount`, `status`, `registered_at`) VALUES
(9, 'jobin', 'mamgalore', 'KA09N1876', '500.00', 'Paid', '2025-03-11 10:07:29'),
(11, 'nixon', 'Mangalore', 'KA09N1899', '500.00', 'Paid', '2025-03-14 06:43:43'),
(13, 'joseph', 'Mangalore', 'KA70M6622', '0.00', 'Paid', '2025-03-17 06:27:57'),
(14, 'jobin', 'Mangalore', 'KA02KJ9088', '120.00', 'Paid', '2025-03-18 07:22:59'),
(15, 'james', 'Mangalore', 'KA07N988', '500.00', 'Paid', '2025-03-18 08:02:43'),
(16, 'nithin', 'Mangalore', 'KA09M1243', '500.00', 'Paid', '2025-03-18 08:09:26'),
(17, 'nithin', 'Mangalore', 'MH1Z2DE1433 ', '400.00', 'Paid', '2025-03-21 09:29:18');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `vehicle_registration`
--
ALTER TABLE `vehicle_registration`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `vehicle_number` (`vehicle_number`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
--
-- AUTO_INCREMENT for table `vehicle_registration`
--
ALTER TABLE `vehicle_registration`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
