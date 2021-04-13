abi = '''[
	{
		"inputs": [
			{
				"internalType": "int256",
				"name": "bp",
				"type": "int256"
			},
			{
				"internalType": "int256",
				"name": "sp",
				"type": "int256"
			}
		],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "partner",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "int256",
				"name": "amountPayed",
				"type": "int256"
			},
			{
				"indexed": false,
				"internalType": "int256",
				"name": "credit",
				"type": "int256"
			}
		],
		"name": "contractPay",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "producer",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "int256",
				"name": "offeredEnergy",
				"type": "int256"
			},
			{
				"indexed": false,
				"internalType": "int256",
				"name": "sellPrice",
				"type": "int256"
			}
		],
		"name": "enterEvent",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "int256",
				"name": "dCover",
				"type": "int256"
			},
			{
				"indexed": false,
				"internalType": "int256",
				"name": "dCoverPricePerUnit",
				"type": "int256"
			},
			{
				"indexed": false,
				"internalType": "int256",
				"name": "batteryDelta",
				"type": "int256"
			},
			{
				"indexed": false,
				"internalType": "int256",
				"name": "bLoad",
				"type": "int256"
			},
			{
				"indexed": false,
				"internalType": "int256",
				"name": "bPricePerUnit",
				"type": "int256"
			},
			{
				"indexed": false,
				"internalType": "int256",
				"name": "oDelta",
				"type": "int256"
			},
			{
				"indexed": false,
				"internalType": "int256",
				"name": "oBp",
				"type": "int256"
			},
			{
				"indexed": false,
				"internalType": "int256",
				"name": "oSp",
				"type": "int256"
			}
		],
		"name": "generalInfo",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "matched",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "int256",
				"name": "matchedEnergy",
				"type": "int256"
			},
			{
				"indexed": false,
				"internalType": "int256",
				"name": "creditChange",
				"type": "int256"
			}
		],
		"name": "matchEvent",
		"type": "event"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "coverCredit",
		"outputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "drainContract",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"internalType": "int256",
				"name": "enteredEnergy",
				"type": "int256"
			},
			{
				"internalType": "int256",
				"name": "sPrice",
				"type": "int256"
			}
		],
		"name": "enterEnergy",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "getBatteryLoad",
		"outputs": [
			{
				"internalType": "int256",
				"name": "",
				"type": "int256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "getBatteryPricePerUnit",
		"outputs": [
			{
				"internalType": "int256",
				"name": "",
				"type": "int256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "getBuyPrice",
		"outputs": [
			{
				"internalType": "int256",
				"name": "",
				"type": "int256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "getContractFunds",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "getCredit",
		"outputs": [
			{
				"internalType": "int256",
				"name": "",
				"type": "int256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"internalType": "address",
				"name": "ofAddr",
				"type": "address"
			}
		],
		"name": "getMatchBlock",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "getSellPrice",
		"outputs": [
			{
				"internalType": "int256",
				"name": "",
				"type": "int256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"internalType": "address",
				"name": "account",
				"type": "address"
			}
		],
		"name": "getSpecCredit",
		"outputs": [
			{
				"internalType": "int256",
				"name": "",
				"type": "int256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "getTotalBatteryPrice",
		"outputs": [
			{
				"internalType": "int256",
				"name": "",
				"type": "int256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"internalType": "address",
				"name": "ofAddr",
				"type": "address"
			}
		],
		"name": "getUpdateBlock",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "matchOrders",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "repairBlockNumbers",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"internalType": "int256",
				"name": "newCredit",
				"type": "int256"
			}
		],
		"name": "setAllCredits",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"internalType": "int256",
				"name": "newCap",
				"type": "int256"
			}
		],
		"name": "setBatteryCapacity",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"internalType": "int8",
				"name": "newEff",
				"type": "int8"
			}
		],
		"name": "setBatteryEff",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"internalType": "int256",
				"name": "newLoad",
				"type": "int256"
			}
		],
		"name": "setBatteryLoad",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"internalType": "int256",
				"name": "newPrice",
				"type": "int256"
			}
		],
		"name": "setBuyPrice",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"internalType": "int256",
				"name": "newPrice",
				"type": "int256"
			}
		],
		"name": "setSellPrice",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"internalType": "int256",
				"name": "nPr",
				"type": "int256"
			}
		],
		"name": "setTotalBatPrice",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	}
]'''