import os, sys
import sklearn
from sklearn import *
import numpy as np
import cPickle
from sklearn.cross_validation import KFold

rf = cPickle.load(open('rf-f1_weighted.pickle', 'r'))
X = cPickle.load(open('X.pickle', 'r'))
y = cPickle.load(open('y.pickle', 'r'))
ids = ['001', '006', '008', '009', '010', '014', '015', '016', '017', '018', '020', '022', '025', '028', '031', '035', '037', '042', '044', '049', '050', '051', '052', '055', '056', '057', '058', '060', '061', '064', '066', '068', '070', '072', '078', '079', '083', '085', '091', '094', '099', '100', '101', '105', '109', '112', '113', '114', '116', '120', '123', '126', '128', '129', '130', '131', '136', '139', '140', '141', '142', '144', '145', '149', '150', '153', '163', '164', '166', '168', '169', '170', '171', '173', '176', '177', '180', '182', '183', '184', '188', '190', '191', '196', '198', '201', '203', '204', '205', '209', '210', '212', '213', '214', '216', '217', '218', '220', '221', '222', '224', '228', '232', '234', '235', '236', '241', '242', '246', '247', '248', '250', '252', '254', '256', '258', '259', '260', '261', '263', '264', '266', '267', '269', '272', '273', '276', '277', '278', '282', '284', '289', '290', '292', '295', '299', '302', '304', '307', '309', '312', '313', '314', '315', '316', '318', '319', '321', '326', '327', '329', '332', '334', '335', '338', '339', '341', '342', '343', '344', '345', '346', '347', '348', '350', '351', '352', '353', '355', '356', '359', '362', '363', '365', '366', '368', '371', '372', '375', '377', '378', '383', '386', '387', '393', '397', '399', '401', '403', '404', '405', '406', '407', '411', '415', '417', '418', '421', '422', '426', '427', '428', '430', '433', '435', '436', '441', '444', '445', '447', '452', '453', '454', '455', '456', '460', '461', '463', '464', '465', '467', '468', '471', '472', '474', '475', '476', '477', '480', '481', '486', '487', '488', '491', '493', '496', '002', '003', '004', '005', '011', '013', '021', '024', '026', '027', '032', '034', '038', '039', '040', '043', '048', '054', '065', '071', '073', '074', '076', '082', '086', '087', '088', '090', '092', '093', '095', '098', '102', '103', '107', '111', '115', '117', '118', '119', '134', '135', '143', '146', '148', '151', '154', '156', '157', '174', '179', '181', '185', '189', '199', '200', '202', '208', '211', '223', '225', '226', '231', '238', '239', '243', '244', '253', '271', '281', '283', '286', '287', '293', '296', '297', '300', '303', '310', '311', '320', '322', '323', '324', '336', '337', '364', '370', '380', '381', '382', '390', '394', '396', '398', '400', '402', '414', '424', '429', '431', '434', '437', '439', '443', '448', '449', '462', '478', '479', '484', '489', '490', '495', '497', '498', '500', '007', '012', '019', '023', '029', '030', '033', '036', '041', '045', '046', '047', '053', '059', '062', '063', '067', '069', '075', '077', '080', '081', '084', '089', '096', '097', '104', '106', '108', '110', '121', '122', '124', '125', '127', '132', '133', '137', '138', '147', '152', '155', '158', '159', '160', '161', '162', '165', '167', '172', '175', '178', '186', '187', '192', '193', '194', '195', '197', '206', '207', '215', '219', '227', '229', '230', '233', '237', '240', '245', '249', '251', '255', '257', '262', '265', '268', '270', '274', '275', '279', '280', '285', '288', '291', '294', '298', '301', '305', '306', '308', '317', '325', '328', '330', '331', '333', '340', '349', '354', '357', '358', '360', '361', '367', '369', '373', '374', '376', '379', '384', '385', '388', '389', '391', '392', '395', '408', '409', '410', '412', '413', '416', '419', '420', '423', '425', '432', '438', '440', '442', '446', '450', '451', '457', '458', '459', '466', '469', '470', '473', '482', '483', '485', '492', '494', '499']

kf = KFold(len(X), n_folds=3, shuffle=True)

out = open('output-kfold.csv', 'wb')
ids = np.array(ids)
y = np.array(y)
rf.set_params(verbose=1, n_jobs=-1)
for k, (train, test) in enumerate(kf):
    print "On fold ", k
    print "\t", len(X[train]), len(X[test])
    rf.fit(X[train], y[train])
    pred = rf.predict(X[test])
    true = y[test]
    cvids = ids[test]
    for i, x in enumerate(cvids):
        out.write(x + ',' + str(true[i]) + ',' + str(pred[i]) + '\n')
        print(x + ',' + str(true[i]) + ',' + str(pred[i]))

out.close()
