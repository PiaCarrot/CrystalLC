	object_const_def
	const CHERRYGROVEMART_CLERK
	const CHERRYGROVEMART_COOLTRAINER_M
	const CHERRYGROVEMART_YOUNGSTER
	const CHERRYGROVEMART_LP_CLERK
	const CHERRYGROVEMART_MOVETUTOR

CherrygroveMart_MapScripts:
	def_scene_scripts

	def_callbacks

CherrygroveMartClerkScript:
	opentext
	checkevent EVENT_GAVE_MYSTERY_EGG_TO_ELM
	iftrue .PokeBallsInStock
	pokemart MARTTYPE_STANDARD, MART_CHERRYGROVE
	closetext
	end

.PokeBallsInStock:
	pokemart MARTTYPE_STANDARD, MART_CHERRYGROVE_DEX
	closetext
	end

CherrygroveMartCooltrainerMScript:
	faceplayer
	opentext
	checkevent EVENT_GAVE_MYSTERY_EGG_TO_ELM
	iftrue .PokeBallsInStock
	writetext CherrygroveMartCooltrainerMText
	waitbutton
	closetext
	end

.PokeBallsInStock:
	writetext CherrygroveMartCooltrainerMText_PokeBallsInStock
	waitbutton
	closetext
	end

CherrygroveMartYoungsterScript:
	jumptextfaceplayer CherrygroveMartYoungsterText

CherrygroveMartLPClerkScript:
	faceplayer
	opentext
	writetext CherrygroveMartLPClerkText
	waitbutton
	pokemart MARTTYPE_LP, MART_CHERRYGROVE
	closetext
	end

CherrygroveMartMoveTutorScript:
	faceplayer
	opentext
	writetext CherrygroveMartMoveTutorIntroText
	yesorno
	iffalse .Refused
	writetext CherrygroveMartMoveTutorAsk500LPOkayText
	yesorno
	iffalse .Refused
	checkmoney YOUR_LP, 500
	ifequal HAVE_LESS, .NotEnoughLP
	setval MOVETUTOR_WATER_GUN
	writetext CherrygroveMartMoveTutorMoveText
	special MoveTutor
	ifequal FALSE, .TeachMove
	sjump .Incompatible

.TeachMove:
	writetext CherrygroveMartMoveTutorSuccessText
	promptbutton
	takemoney YOUR_LP, 500
	playsound SFX_TRANSACTION
	waitsfx
	writetext CherrygroveMartMoveTutorDoneText
	waitbutton
	closetext
	end

.Incompatible:
	writetext CherrygroveMartMoveTutorIncompatibleText
	waitbutton
	closetext
	end

.Refused:
	writetext CherrygroveMartMoveTutorRefusedText
	waitbutton
	closetext
	end

.NotEnoughLP:
	writetext CherrygroveMartMoveTutorNotEnoughLPText
	waitbutton
	closetext
	end

CherrygroveMartCooltrainerMText:
	text "They're fresh out"
	line "of # BALLS!"

	para "When will they get"
	line "more of them?"
	done

CherrygroveMartCooltrainerMText_PokeBallsInStock:
	text "# BALLS are in"
	line "stock! Now I can"
	cont "catch #MON!"
	done

CherrygroveMartYoungsterText:
	text "When I was walking"
	line "in the grass, a"

	para "bug #MON poi-"
	line "soned my #MON!"

	para "I just kept going,"
	line "but then my"
	cont "#MON fainted."

	para "You should keep an"
	line "ANTIDOTE with you."
	done

CherrygroveMartLPClerkText:
	text "I'm testing our LP"
	line "held item stock."

	para "Take a look!"
	done

CherrygroveMartMoveTutorIntroText:
	text "Hey! I can teach"
	line "WATER GUN."

	para "Want your #MON"
	line "to learn it?"
	done

CherrygroveMartMoveTutorAsk500LPOkayText:
	text "It costs 500 LP."
	line "Sound good?"
	done

CherrygroveMartMoveTutorRefusedText:
	text "No worries. Come"
	line "back anytime."
	done

CherrygroveMartMoveTutorMoveText:
	text "WATER GUN is a"
	line "solid move."
	done

CherrygroveMartMoveTutorSuccessText:
	text "Great choice!"
	done

CherrygroveMartMoveTutorDoneText:
	text "There! Enjoy your"
	line "new move."
	done

CherrygroveMartMoveTutorIncompatibleText:
	text "Hmm… This #MON"
	line "can't learn it."
	done

CherrygroveMartMoveTutorNotEnoughLPText:
	text "You need more LP."
	done

CherrygroveMart_MapEvents:
	db 0, 0 ; filler

	def_warp_events
	warp_event  2,  7, CHERRYGROVE_CITY, 1
	warp_event  3,  7, CHERRYGROVE_CITY, 1

	def_coord_events

	def_bg_events

	def_object_events
	object_event  1,  3, SPRITE_CLERK, SPRITEMOVEDATA_STANDING_RIGHT, 0, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, CherrygroveMartClerkScript, -1
	object_event  7,  6, SPRITE_COOLTRAINER_M, SPRITEMOVEDATA_WALK_LEFT_RIGHT, 2, 0, -1, -1, 0, OBJECTTYPE_SCRIPT, 0, CherrygroveMartCooltrainerMScript, -1
	object_event  2,  5, SPRITE_YOUNGSTER, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, PAL_NPC_RED, OBJECTTYPE_SCRIPT, 0, CherrygroveMartYoungsterScript, -1
	object_event  5,  3, SPRITE_CLERK, SPRITEMOVEDATA_STANDING_DOWN, 0, 0, -1, -1, PAL_NPC_BLUE, OBJECTTYPE_SCRIPT, 0, CherrygroveMartLPClerkScript, -1
	object_event  7,  3, SPRITE_SUPER_NERD, SPRITEMOVEDATA_STANDING_LEFT, 0, 0, -1, -1, PAL_NPC_BROWN, OBJECTTYPE_SCRIPT, 0, CherrygroveMartMoveTutorScript, -1
