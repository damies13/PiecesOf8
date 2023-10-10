# PiecesOf8
Experimental POS Crypto Currency in Python

## Structure

First block

```
{
	block_id: "0-0",
	previous_hash: "88888888",
	block_creator: "0123456789abcdef",
	block_stakers: ["damies13"],
	nonce: 13,
	transaction_list: [
		{
			type: "server",
			uuid: "01ff2a4f-9b32-446b-ba78-578cabbdacda",
			owner: "865a2c37-e530-4c8c-9dda-bc555246b79e"
			},
		{
			type: "user",
			username: "damies13",
			uuid:	"865a2c37-e530-4c8c-9dda-bc555246b79e"
			icon: b'base64 image data',
			public_key: [b'-----BEGIN PUBLIC KEY-----', b'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxp6zrAuh3AgJO88hFEvK', b'0BCQ6S0AEO5M7pvRpp0JRobGK9sSfmQwRdfUo0gDQBNVsse3DzqnUP7w4XXeJ/iG', b'+CGmta/wOHj11X5vZo9zBrPMtO1TLQ488IxpTSkw+a5fNBaT0jepUjMi5uNMP6Io', b'dTYu60Ng4qd8GR+l26jPBSsZOrzOEWx4JUaY0PcXoetpSFytQ9x0tMW4mHt3vCWr', b'IrGxXfZjZWUVDc2kt8WLk1DEzEDNGEAFALANXgvNV7/BzTGaBmNVlrFn8GUgRfHM', b'Pu60IrGw5ENHMbvlA5+or1SdXkrBEXrt0myh/WsJccpkcmRL5O3+8+fWlDKcWfyk', b'SwIDAQAB', b'-----END PUBLIC KEY-----'],
			private_data: b' encrypted data, use password to open'
			},
		{
			type: "coin",
			from: None,
			to: "865a2c37-e530-4c8c-9dda-bc555246b79e",
			amount: "8888888888888888"
			},
		{
			type: "stake",
			staker: "865a2c37-e530-4c8c-9dda-bc555246b79e",
			with: "01ff2a4f-9b32-446b-ba78-578cabbdacda",
			amount: "88888888"
			},
	],
	hash: "0123456789abcdef888"
}
```

## Block Rules

These are the rules the Transactors need to follow for creating blocks

	1. Server must have been online for 24 hours
	2. Server must have coins staked for to create blocks
	3. minimum stake size is 88 coins
	4. Total value of all transactions cannot exceed total value of staked coins
	5. 1 coin has a nominal value of 1 gram of gold
	6. Transaction fees:
		- 1% of transaction value, paid by sender
			- 50% of fee is paid to stakers
			- 50% of fee is paid as tax to PiecesOf8 foundation
		- 1% of of fee is created as new coin and paid to server owner
	7. Free transactions:
		- user (create / update)
		- server  (create / update)
	8. Full price Transactions
		- coin transfer
		- sales
		- Product Registration
			- must include a Bill of materials (BOM) for cost calculation
			- labour should be included in the BOM unless fully imported product
			- Any transaction fees paid on BOM items can be deducted from registration fee
	9. Server confirms all transactions are validated and signs block before proposing
	10. Server starts with a nonce of 0 and increments the nonce until the block hash ends with 888
	11. block must contain a minimum of 3 transactions
	12. block must be created no less than 10 seconds after previous block
	13. Server may propose new block if:
	 - Any server if there are less than 32 servers
	 - last digit of servers uuid matches digit announced by previous block creator when > 32 and < 1024 servers
	 - last 2 digits of servers uuid matches digits announced by previous block creator when > 1024 and < 32768 servers
	 - last 3 digits of servers uuid matches digits announced by previous block creator when > 32768 and < 1048576 servers

## Server

These are the "servers" of PiecesOf8, servers can:
 - on start-up should validate the block chain
 - receive transactions from clients into the transaction queue
 - transmit transaction queue updates to other servers
 - propose blocks according to the block rules
 - Advertise availability to other servers
 - support clients and other servers by providing data as requested
 - Transactions should be validated before adding to queue
 - if server is last bock creator:
 	- select and announce filter digits based on block rules
 	- wait for proposed blocks, minimum 30 seconds maximum 60 seconds after first proposed block
	- if more than 1 valid proposed block select one at random

## Client

Clients can:
 - create transactions
 - validate blocks/chain to establish confidence in network and connected servers

## Users

###	Create User
 - Check username not exists
 - assign uuid
 - set password (check strength)
 - Create private_key and public_key
 - submit create user record with
   - username and public_key accessible
	 - private_key password encrypted

###	User Login
 - use password to decrypt the private_key

## Coin Transfer

	- Sender initiated transaction
		- transaction UUID
		- Sender UUID
		- Receiver UUID
		- Amount
		- Sender Signature

	- Receiver initiated transaction
		- Receiver creates transaction
			- transaction UUID
			- Sender UUID
			- Receiver UUID
			- Amount
			- Receiver Signature
		- Sender updates transaction with
			- Sender Signature
			- confirm : True / False

## Sales

- Receiver creates transaction
	- Transaction UUID
	- Sender UUID
	- Receiver UUID
	- Amount
	- Product list (products must be preregistered existing items, unless product is labour)
	- Receiver Signature
- Sender updates transaction with
	- Sender Signature
	- confirm : True / False

## Product Registration

	- Product UUID
	- Product description
	- Serial Number
	- BOM












draft
