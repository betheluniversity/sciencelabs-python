class ReportController:
    math_lab_cumulative = {
        '2004': {'academicYear': '2003-2004', 'monthly': (0, 28, 291, 328, 394, 196, 0, 0, 0, 379, 425, 346, 76, 28),
                 'springTotal': 1209, 'fallTotal': 1226, 'summerTotal': 0, 'yearTotal': 2463},
        '2003': {'academicYear': '2002-2003', 'monthly': (0, 19, 187, 234, 273, 155, 0, 0, 0, 167, 274, 215, 47),
                 'springTotal': 849, 'fallTotal': 703, 'summerTotal': 0, 'yearTotal': 1571},
        '2002': {'academicYear': '2001-2002', 'monthly': (0, 36, 132, 135, 226, 121, 0, 0, 0, 225, 238, 192, 50),
                 'springTotal': 614, 'fallTotal': 705, 'summerTotal': 0, 'yearTotal': 1355},
        '2001': {'academicYear': '2000-2001', 'monthly': (0, 0, 146, 157, 153, 49, 0, 0, 0, 222, 337, 226, 71),
                 'springTotal': 505, 'fallTotal': 856, 'summerTotal': 0, 'yearTotal': 1361},
        '2000': {'academicYear': '1999-2000', 'monthly': (0, 0, 143, 183, 194, 133, 0, 0, 0, 203, 262, 259, 59),
                 'springTotal': 653, 'fallTotal': 783, 'summerTotal': 0, 'yearTotal': 1436},
        '1999': {'academicYear': '1998-1999', 'monthly': (0, 0, 61, 107, 106, 56, 0, 0, 0, 123, 156, 116, 42),
                 'springTotal': 330, 'fallTotal': 437, 'summerTotal': 0, 'yearTotal': 767},
        '1998': {'academicYear': '1997-1998', 'monthly': (0, 0, 65, 60, 51, 16, 0, 0, 0, 88, 146, 99, 27),
                 'springTotal': 192, 'fallTotal': 360, 'summerTotal': 0, 'yearTotal': 552},
        '1997': {'academicYear': '1996-1997', 'monthly': (0, 0, 81, 144, 191, 49, 0, 0, 0, 153, 175, 117, 12),
                 'springTotal': 465, 'fallTotal': 457, 'summerTotal': 0, 'yearTotal': 922},
        '1996': {'academicYear': '1995-1996', 'monthly': (0, 0, 104, 83, 93, 27, 0, 0, 0, 138, 245, 208, 42),
                 'springTotal': 307, 'fallTotal': 633, 'summerTotal': 0, 'yearTotal': 940},
        '1995': {'academicYear': '1994-1995', 'monthly': (0, 0, 103, 84, 93, 31, 0, 0, 0, 95, 96, 88, 20),
                 'springTotal': 311, 'fallTotal': 299, 'summerTotal': 0, 'yearTotal': 610},
        '1994': {'academicYear': '1993-1994', 'monthly': (0, 0, 85, 100, 93, 29, 0, 0, 0, 136, 150, 131, 50),
                 'springTotal': 307, 'fallTotal': 467, 'summerTotal': 0, 'yearTotal': 774},
        '1993': {'academicYear': '1992-1993', 'monthly': (0, 0, 90, 58, 80, 32, 0, 0, 0, 98, 99, 69, 14),
                 'springTotal': 260, 'fallTotal': 280, 'summerTotal': 0, 'yearTotal': 540}
    }

    cs_lab_cumulative = {
        '2007': {'academicYear': '2006-2007', 'monthly': (0, 17, 40, 48, 28, 0, 0, 0, 0, 0, 0, 0, 0),
                 'springTotal': 133, 'fallTotal': 0, 'summerTotal': 0, 'yearTotal': 133},
        '2006': {'academicYear': '2005-2006', 'monthly': (0, 22, 43, 49, 68, 0, 0, 0, 0, 0, 0, 0, 0),
                 'springTotal': 182, 'fallTotal': 0, 'summerTotal': 0, 'yearTotal': 182},
        '2005': {'academicYear': '2004-2005', 'monthly': (0, 25, 36, 46, 26, 0, 0, 0, 0, 0, 0, 0, 0),
                 'springTotal': 133, 'fallTotal': 0, 'summerTotal': 0, 'yearTotal': 133},
        '2004': {'academicYear': '2003-2004', 'monthly': (0, 22, 29, 43, 16, 0, 0, 0, 0, 0, 0, 0, 0),
                 'springTotal': 110, 'fallTotal': 0, 'summerTotal': 0, 'yearTotal': 110},
        '2003': {'academicYear': '2002-2003', 'monthly': (0, 12, 16, 33, 4, 0, 0, 0, 0, 0, 0, 0, 0),
                 'springTotal': 65, 'fallTotal': 0, 'summerTotal': 0, 'yearTotal': 65},
        '2002': {'academicYear': '2001-2002', 'monthly': (0, 6, 9, 49, 20, 0, 0, 0, 0, 0, 0, 0, 0),
                 'springTotal': 84, 'fallTotal': 0, 'summerTotal': 0, 'yearTotal': 84},
        '2001': {'academicYear': '2000-2001', 'monthly': (0, 53, 13, 40, 12, 0, 0, 0, 0, 0, 0, 0, 0),
                 'springTotal': 118, 'fallTotal': 0, 'summerTotal': 0, 'yearTotal': 118}
    }

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']

    days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
