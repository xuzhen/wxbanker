#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    https://launchpad.net/wxbanker
#    currencies.py: Copyright 2007-2009 Mike Rooney <michael@wxbanker.org>
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
#    along with wxBanker.  If not, see <http://www.gnu.org/licenses/>.%

import unittest, os

import controller, wxbanker

class CurrencyTests(unittest.TestCase):
    def testCurrencyDisplay(self):
        import currencies as c
        self.assertEquals(c.LocalizedCurrency().float2str(1), u'$1.00')
        self.assertEquals(c.UnitedStatesCurrency().float2str(1), u'$1.00')
        self.assertEquals(c.EuroCurrency().float2str(1), u'1.00 €')
        self.assertEquals(c.GreatBritainCurrency().float2str(1), u'£1.00')
        self.assertEquals(c.JapaneseCurrency().float2str(1), u'￥1')
        self.assertEquals(c.RussianCurrency().float2str(1), u'1.00 руб')
    
class ModelTests(unittest.TestCase):
    def setUp(self):
        if os.path.exists("test.db"):
            os.remove("test.db")
        self.Controller = controller.Controller("test.db")
    
    def testNewAccountIsSameCurrencyAsOthers(self):
        # This test is only valid so long as only one currency is allowed.
        # Otherwise it needs to test a new account gets the right default currency, probably Localized
        import currencies
        model = self.Controller.Model
        
        account = model.CreateAccount("Hello")
        self.assertEqual(account.Currency, currencies.LocalizedCurrency())
        
        account.Currency = currencies.EuroCurrency()
        self.assertEqual(account.Currency, currencies.EuroCurrency())
        
        account2 = model.CreateAccount("Another!")
        self.assertEqual(account2.Currency, currencies.EuroCurrency())
        
    def tearDown(self):
        if os.path.exists("test.db"):
            os.remove("test.db")
            
            
class GUITests(unittest.TestCase):
    def setUp(self):
        self.ConfigPath = os.path.expanduser("~/.wxBanker")
        self.ConfigPathBackup = self.ConfigPath + ".backup"
        if os.path.exists("test.db"):
            os.remove("test.db")
        if os.path.exists(self.ConfigPath):
            os.rename(self.ConfigPath, self.ConfigPathBackup)
        
        self.App = wxbanker.init("test.db")
        self.Frame = self.App.TopWindow
        
    def testAutoSaveSetAndSaveDisabled(self):
        self.assertTrue( self.Frame.MenuBar.autoSaveMenuItem.IsChecked() )
        self.assertFalse( self.Frame.MenuBar.saveMenuItem.IsEnabled() )
    
    def tearDown(self):
        if os.path.exists("test.db"):
            os.remove("test.db")
        if os.path.exists(self.ConfigPathBackup):
            os.rename(self.ConfigPathBackup, self.ConfigPath)
        

if __name__ == '__main__':
    unittest.main()