#   PluginName:  Battery 4
#   Created by:  NFX
# 
from fireNFX_Classes import TnfxParameter, TnfxChannelPlugin, cpChannelPlugin, cpMixerPlugin
from fireNFX_PluginDefs import USER_PLUGINS
pluginBattery4 = TnfxChannelPlugin('Battery 4', '', cpChannelPlugin)
pluginBattery4.InvertOctaves = True
if(pluginBattery4.Name not in USER_PLUGINS.keys()):
    USER_PLUGINS[pluginBattery4.Name] = pluginBattery4
    print('Battery 4 parameter definitions loaded.')
 
pluginBattery4.addParamToGroup('ALL', TnfxParameter(0, '#000', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(1, '#001', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(2, '#002', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(3, '#003', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4, '#004', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(5, '#005', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(6, '#006', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(7, '#007', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(8, '#008', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(9, '#009', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(10, '#010', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(11, '#011', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(12, '#012', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(13, '#013', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(14, '#014', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(15, '#015', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(16, '#016', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(17, '#017', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(18, '#018', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(19, '#019', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(20, '#020', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(21, '#021', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(22, '#022', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(23, '#023', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(24, '#024', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(25, '#025', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(26, '#026', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(27, '#027', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(28, '#028', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(29, '#029', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(30, '#030', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(31, '#031', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(32, '#032', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(33, '#033', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(34, '#034', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(35, '#035', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(36, '#036', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(37, '#037', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(38, '#038', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(39, '#039', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(40, '#040', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(41, '#041', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(42, '#042', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(43, '#043', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(44, '#044', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(45, '#045', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(46, '#046', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(47, '#047', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(48, '#048', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(49, '#049', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(50, '#050', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(51, '#051', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(52, '#052', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(53, '#053', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(54, '#054', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(55, '#055', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(56, '#056', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(57, '#057', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(58, '#058', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(59, '#059', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(60, '#060', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(61, '#061', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(62, '#062', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(63, '#063', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(64, '#064', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(65, '#065', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(66, '#066', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(67, '#067', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(68, '#068', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(69, '#069', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(70, '#070', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(71, '#071', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(72, '#072', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(73, '#073', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(74, '#074', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(75, '#075', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(76, '#076', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(77, '#077', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(78, '#078', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(79, '#079', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(80, '#080', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(81, '#081', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(82, '#082', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(83, '#083', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(84, '#084', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(85, '#085', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(86, '#086', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(87, '#087', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(88, '#088', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(89, '#089', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(90, '#090', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(91, '#091', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(92, '#092', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(93, '#093', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(94, '#094', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(95, '#095', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(96, '#096', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(97, '#097', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(98, '#098', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(99, '#099', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(100, '#100', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(101, '#101', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(102, '#102', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(103, '#103', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(104, '#104', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(105, '#105', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(106, '#106', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(107, '#107', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(108, '#108', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(109, '#109', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(110, '#110', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(111, '#111', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(112, '#112', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(113, '#113', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(114, '#114', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(115, '#115', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(116, '#116', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(117, '#117', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(118, '#118', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(119, '#119', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(120, '#120', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(121, '#121', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(122, '#122', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(123, '#123', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(124, '#124', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(125, '#125', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(126, '#126', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(127, '#127', 0, 'n/a ', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4096, 'MIDI CC #0 (Bank select MSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4097, 'MIDI CC #1 (Modulation wheel)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4098, 'MIDI CC #2 (Breath controller)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4099, 'MIDI CC #3', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4100, 'MIDI CC #4 (Foot controller)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4101, 'MIDI CC #5 (Portamento time)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4102, 'MIDI CC #6 (Data entry MSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4103, 'MIDI CC #7 (Main volume)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4104, 'MIDI CC #8 (Balance)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4105, 'MIDI CC #9', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4106, 'MIDI CC #10 (Pan)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4107, 'MIDI CC #11 (Expression controller)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4108, 'MIDI CC #12 (Control 1)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4109, 'MIDI CC #13 (Control 2)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4110, 'MIDI CC #14', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4111, 'MIDI CC #15', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4112, 'MIDI CC #16 (General purpose controller 1)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4113, 'MIDI CC #17 (General purpose controller 2)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4114, 'MIDI CC #18 (General purpose controller 3)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4115, 'MIDI CC #19 (General purpose controller 4)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4116, 'MIDI CC #20', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4117, 'MIDI CC #21', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4118, 'MIDI CC #22', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4119, 'MIDI CC #23', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4120, 'MIDI CC #24', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4121, 'MIDI CC #25', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4122, 'MIDI CC #26', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4123, 'MIDI CC #27', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4124, 'MIDI CC #28', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4125, 'MIDI CC #29', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4126, 'MIDI CC #30', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4127, 'MIDI CC #31', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4128, 'MIDI CC #32 (Bank select LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4129, 'MIDI CC #33 (Modulation wheel LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4130, 'MIDI CC #34 (Breath controller LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4131, 'MIDI CC #35', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4132, 'MIDI CC #36 (Foot controller LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4133, 'MIDI CC #37 (Portamento time LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4134, 'MIDI CC #38 (Data entry LSB )', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4135, 'MIDI CC #39 (Main volume LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4136, 'MIDI CC #40 (Balance LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4137, 'MIDI CC #41', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4138, 'MIDI CC #42 (Pan LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4139, 'MIDI CC #43 (Expression controller LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4140, 'MIDI CC #44 (Control 1 LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4141, 'MIDI CC #45 (Control 2 LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4142, 'MIDI CC #46', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4143, 'MIDI CC #47', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4144, 'MIDI CC #48 (General purpose controller 1 LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4145, 'MIDI CC #49 (General purpose controller 2 LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4146, 'MIDI CC #50 (General purpose controller 3 LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4147, 'MIDI CC #51 (General purpose controller 4 LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4148, 'MIDI CC #52', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4149, 'MIDI CC #53', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4150, 'MIDI CC #54', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4151, 'MIDI CC #55', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4152, 'MIDI CC #56', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4153, 'MIDI CC #57', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4154, 'MIDI CC #58', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4155, 'MIDI CC #59', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4156, 'MIDI CC #60', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4157, 'MIDI CC #61', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4158, 'MIDI CC #62', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4159, 'MIDI CC #63', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4160, 'MIDI CC #64 (Damper pedal (sustain))', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4161, 'MIDI CC #65 (Portamento)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4162, 'MIDI CC #66 (Sostenuto)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4163, 'MIDI CC #67 (Soft pedal)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4164, 'MIDI CC #68 (Legato footswitch)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4165, 'MIDI CC #69 (Hold 2)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4166, 'MIDI CC #70 (Sound variation)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4167, 'MIDI CC #71 (Harmonic content)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4168, 'MIDI CC #72 (Release time)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4169, 'MIDI CC #73 (Attack time)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4170, 'MIDI CC #74 (Brightness)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4171, 'MIDI CC #75 (Sound controller 6)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4172, 'MIDI CC #76 (Sound controller 7)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4173, 'MIDI CC #77 (Sound controller 8)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4174, 'MIDI CC #78 (Sound controller 9)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4175, 'MIDI CC #79 (Sound controller 10)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4176, 'MIDI CC #80 (General purpose controller 5)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4177, 'MIDI CC #81 (General purpose controller 6)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4178, 'MIDI CC #82 (General purpose controller 7)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4179, 'MIDI CC #83 (General purpose controller 8)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4180, 'MIDI CC #84 (Portamento control)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4181, 'MIDI CC #85', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4182, 'MIDI CC #86', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4183, 'MIDI CC #87', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4184, 'MIDI CC #88', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4185, 'MIDI CC #89', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4186, 'MIDI CC #90', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4187, 'MIDI CC #91 (Reverb depth)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4188, 'MIDI CC #92 (Tremolo depth)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4189, 'MIDI CC #93 (Chorus depth)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4190, 'MIDI CC #94 (Celeste depth)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4191, 'MIDI CC #95 (Phaser depth)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4192, 'MIDI CC #96 (Data increment)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4193, 'MIDI CC #97 (Data decrement)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4194, 'MIDI CC #98 (NRPN LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4195, 'MIDI CC #99 (NRPN MSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4196, 'MIDI CC #100 (RPN LSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4197, 'MIDI CC #101 (RPN MSB)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4198, 'MIDI CC #102', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4199, 'MIDI CC #103', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4200, 'MIDI CC #104', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4201, 'MIDI CC #105', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4202, 'MIDI CC #106', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4203, 'MIDI CC #107', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4204, 'MIDI CC #108', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4205, 'MIDI CC #109', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4206, 'MIDI CC #110', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4207, 'MIDI CC #111', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4208, 'MIDI CC #112', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4209, 'MIDI CC #113', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4210, 'MIDI CC #114', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4211, 'MIDI CC #115', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4212, 'MIDI CC #116', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4213, 'MIDI CC #117', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4214, 'MIDI CC #118', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4215, 'MIDI CC #119', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4216, 'MIDI CC #120 (All sound off)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4217, 'MIDI CC #121 (Reset all controllers)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4218, 'MIDI CC #122 (Local control on/off)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4219, 'MIDI CC #123 (All notes off)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4220, 'MIDI CC #124 (Omni mode off)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4221, 'MIDI CC #125 (Omni mode on)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4222, 'MIDI CC #126 (Mono mode on)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4223, 'MIDI CC #127 (Poly mode on)', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4224, 'MIDI Channel 1 Aftertouch', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4225, 'MIDI Channel 2 Aftertouch', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4226, 'MIDI Channel 3 Aftertouch', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4227, 'MIDI Channel 4 Aftertouch', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4228, 'MIDI Channel 5 Aftertouch', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4229, 'MIDI Channel 6 Aftertouch', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4230, 'MIDI Channel 7 Aftertouch', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4231, 'MIDI Channel 8 Aftertouch', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4232, 'MIDI Channel 9 Aftertouch', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4233, 'MIDI Channel 10 Aftertouch', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4234, 'MIDI Channel 11 Aftertouch', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4235, 'MIDI Channel 12 Aftertouch', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4236, 'MIDI Channel 13 Aftertouch', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4237, 'MIDI Channel 14 Aftertouch', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4238, 'MIDI Channel 15 Aftertouch', 0, '', False) )
pluginBattery4.addParamToGroup('ALL', TnfxParameter(4239, 'MIDI Channel 16 Aftertouch', 0, '', False) )

# [PARAMETER OFFSETS] 
# Notice, the code lines above contains the text "TnfxParameter(" followed by a number
# That number represents the parameter offset for the parameter described on that line
# You can use the parameter offset number to program your own USER Knob mappings below
# 
# [HOW TO SET CUSTOM KNOB MAPPINGS]
# The assignKnobs() function takes a list of up to 8 parameter offsets.
# The list must be in brackets like this [ 21, 12, 3, 7]. Max 8 offsets in list.
# it assigns them in order from :
#   USER1, KNOBS 1-4 as the first 4 params
#   USER2, KNOBS 1-4 as the second 4 params

# [ENABLING THE CUSTOM MAPPING]
# Comment/Uncomment the next line to disable/enable the knob mappings. 
pluginBattery4.assignKnobs([4096, 4128, 2, 3, 4, 5, 6, 7]) 
 

