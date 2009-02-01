"""
A refactor of TransactionGrid, using ObjectListView.

Can we bind this to the list so inserts and removals and automatically handled?

IMPLEMENTED:
- displaying transactions
- editable amounts/descriptions
- edits pushed to model
- total based on total of last transaction
- handle new transactions
- min column sizes when there aren't any transactions
- default sort by date
- display negative amount as Red
- right-click context menu
  - remove
  - calculator options on amounts
- amount editing as %.2f (instead of 2.16999999 etc)
TODO (for feature parity):
- editable date
- done? totals automatically updates for transaction changes above them
EXTRA:
- custom negative option such as Red, (), or Red and ()
NEW THINGS:
- sorting by columns
- empty account message
"""

import wx, datetime
from wx.lib.pubsub import Publisher
from ObjectListView import GroupListView, ColumnDefn


class TransactionOLV(GroupListView):
    def __init__(self, parent):
        GroupListView.__init__(self, parent, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.CurrentAccount = None
        
        self.showGroups = False
        self.evenRowsBackColor = wx.Color(224,238,238)
        self.oddRowsBackColor = wx.WHITE
        self.rowFormatter = self.rowFormatter2
        self.cellEditMode = GroupListView.CELLEDIT_SINGLECLICK
        self.SetEmptyListMsg("No transactions entered.")
        
        # Calculate the necessary width for the date column.
        dateStr = str(datetime.date.today())
        dateWidth = self.GetTextExtent(dateStr)[0] + 10
        
        self.SetColumns([
            ColumnDefn("Date", valueGetter="Date", width=dateWidth),
            ColumnDefn("Description", valueGetter="Description", isSpaceFilling=True),
            ColumnDefn("Amount", "right", valueGetter="Amount", stringConverter=self.renderFloat),
            ColumnDefn("Total", "right", valueGetter=self.getTotal, stringConverter=self.renderFloat, isEditable=False),
        ])
        
        # By default, sort by the date column, ascending.
        self.SortBy(0)
        
        self.Bind(wx.EVT_RIGHT_DOWN, self.onRightDown)
        
    def getTotal(self, transObj):
        """
        A somewhat hackish implementation, but an improvement!
        """
        i = self.GetIndexOf(transObj)
        if i == 0:
            total = transObj.Amount
        else:
            previousObj = self.GetObjectAt(i-1)
            try:
                previousTotal = previousObj._Total
            except AttributeError:
                previousTotal = self.getTotal(previousObj)
            
            total = previousTotal + transObj.Amount
                
        transObj._Total = total
        return total
    
    def rowFormatter2(self, listItem, transaction):
        if transaction.Amount < 0:
            listItem.SetTextColour(wx.RED)
    
    def renderFloat(self, floatVal):
        return self.CurrentAccount.float2str(floatVal)
    
    def setAccount(self, account, scrollToBottom=True):
        self.CurrentAccount = account
        
        if account is None:
            transactions = []
        else:
            transactions = account.Transactions
        
        self.Parent.Freeze()
        self.SetObjects(transactions)
        wx.CallLater(50, self.frozenResize) # Necessary for columns to size properly. (GTK)
        
        Publisher.unsubscribe(self.onTransactionAdded)
        Publisher.unsubscribe(self.onTransactionRemoved)
        
        if account:
            Publisher.subscribe(self.onTransactionAdded, "transaction.created.%s" % account.Name)
            Publisher.subscribe(self.onTransactionRemoved, "transaction.removed.%s" % account.Name)
        
        if scrollToBottom:
            self.ensureVisible(-1)
        
    def ensureVisible(self, index):
        if index < 0:
            index = self.GetItemCount() + index
        self.EnsureCellVisible(index, 0)
        
    def onRightDown(self, event):
        itemID, flag, col = self.HitTestSubItem(event.Position)

        # Don't do anything for right-clicks not on items.
        if itemID == -1:
            return
        
        transaction = self.GetObjectAt(itemID)
        self.showContextMenu(transaction, col)
    
    def showContextMenu(self, transaction, col):
        menu = wx.Menu()

        if col in (2,3):
            # This is an amount cell, allow calculator options.
            actions = [
                (_("Send to calculator"), "wxART_calculator_edit"),
                (_("Add to calculator"), "wxART_calculator_add"),
                (_("Subtract from calculator"), "wxART_calculator_delete"),
            ]

            for actionStr, artHint in actions:
                item = wx.MenuItem(menu, -1, actionStr)
                item.SetBitmap(wx.ArtProvider.GetBitmap(artHint))
                menu.Bind(wx.EVT_MENU, lambda e, s=actionStr: self.onCalculatorAction(transaction, col, s), source=item)
                menu.AppendItem(item)
            menu.AppendSeparator()

        # Always show the Remove context entry.
        removeItem = wx.MenuItem(menu, -1, _("Remove this transaction"))
        menu.Bind(wx.EVT_MENU, lambda e: self.onRemoveTransaction(transaction), source=removeItem)
        removeItem.SetBitmap(wx.ArtProvider.GetBitmap('wxART_delete'))
        menu.AppendItem(removeItem)

        # Show the menu and then destroy it afterwards.
        self.PopupMenu(menu)
        menu.Destroy()

    def onCalculatorAction(self, transaction, col, actionStr):
        """
        Given an action to perform on the calculator, and the row and col,
        generate the string of characters necessary to perform that action
        in the calculator, and push them.
        """
        command = actionStr.split(' ')[0].upper()
        
        if col == 2:
            amount = transaction.Amount
        elif col == 3:
            amount = transaction._Total
        else:
            raise Exception("onCalculatorAction should only be called with col 2 or 3.")

        pushStr = {'SEND': 'C%s', 'SUBTRACT': '-%s=', 'ADD': '+%s='}[command]
        pushStr %= amount

        Publisher.sendMessage("CALCULATOR.PUSH_CHARS", pushStr)

    def onRemoveTransaction(self, transaction):
        """Remove the transaction from the account."""
        self.CurrentAccount.RemoveTransaction(transaction)
        
    def frozenResize(self):
        self.Parent.Layout()
        self.Parent.Thaw()
        
    def onTransactionRemoved(self, message):
        transaction = message.data
        self.Parent.Freeze()
        # Remove the item from the list.
        self.RemoveObject(transaction)
        
        wx.CallLater(50, self.frozenResize) # Necessary for columns to size properly. (GTK)
    
    def onTransactionAdded(self, message):
        transaction = message.data
        self.AddObject(transaction)
        #TODO: Perhaps get the actual position and scroll to that, it may not be last.
        self.ensureVisible(-1)


if __name__ == "__main__":
    app = wx.App(False)
    olvFrame(None).Show()
    app.MainLoop()
