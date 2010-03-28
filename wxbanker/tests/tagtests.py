#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    https://launchpad.net/wxbanker
#    tagtests.py: Copyright 2007-2009 Mike Rooney <mrooney@ubuntu.com>
#
#    This file is part of wxBanker.
#
#    wxBanker is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    wxBanker is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with wxBanker.  If not, see <http://www.gnu.org/licenses/>.

from wxbanker.tests import testbase
from wxbanker.bankobjects.tag import Tag

class TagTests(testbase.TestCaseWithController):
    def testEmptyModelHasNoTags(self):
        self.assertEqual(self.Model.Tags, [])
        
    def testTagStringValue(self):
        tag = Tag(0, "Foobar")
        self.assertEqual(str(tag), "Foobar")
        
    def testTagEquality(self):
        a = Tag(1, "A")
        self.assertEqual(a, a)
        self.assertNotEqual(a, None)
        
        a2 = Tag(2, "A")
        self.assertNotEqual(a, a2)
        
        a3 = Tag(1, "A")
        self.assertEqual(a, a3)
        