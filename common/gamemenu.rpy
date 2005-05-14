# This file contains code for the game menu, and associated
# functionality that looks an awful lot like it.

init -499:
    python:

        ######################################################################
        # First up, we define a bunch of configuration variable, which the
        # user can change.

        # The contents of the game menu choices.
        library.game_menu = [
                ( "return", "Return", ui.jumps("_return"), 'True'),
                ( "prefs", "Preferences", ui.jumps("_prefs_screen"), 'True' ),
                ( "save", "Save Game", ui.jumps("_save_screen"), 'not renpy.context().main_menu' ),
                ( "load", "Load Game", ui.jumps("_load_screen"), 'True'),
                ( "mainmenu", "Main Menu", lambda : _mainmenu_prompt(), 'not renpy.context().main_menu' ),
                ( "quit", "Quit", lambda : _quit_prompt("quit"), 'True' ),
                ]

        # The number of columns of files to show at once.
        library.file_page_cols = 2

        # The number of rows of files to show at once.
        library.file_page_rows = 5

        # The number of pages to add quick access buttons for.
        library.file_quick_access_pages = 5

        # A small amount of padding.
        library.padding = 2

        # The width of a thumbnail.
        library.thumbnail_width = 66

        # The height of a thumbnail.
        library.thumbnail_height = 50

        # Sound played when entering the library without clicking a
        # button.
        library.enter_sound = None

        # Sound played when leaving the library without clicking a
        # button.
        library.exit_sound = None

        # Transition that occurs when entering the game menu.
        library.enter_transition = None

        # Transition that occurs when leaving the game menu.
        library.exit_transition = None

        # This lets us disable the file pager. (So we only have one
        # page of files.)
        library.disable_file_pager = False

        # This lets us disable the thumbnails in the file pager.
        library.disable_thumbnails = False

        # If True, we will be prompted before loading a game. (This can
        # be changed from inside the game code, so that one can load from
        # the first few screens but not after that.)
        _load_prompt = True

        ######################################################################
        # Next, support code.

        # This is used to store scratch data that's used by the
        # library, but shouldn't be saved out as part of the savegame.
        _scratch = object()
            
        # This returns a window containing the game menu navigation
        # buttons, set up to jump to the appropriate screen sections.
        #
        # This can be overridden by user code. It's called with the
        # name of the selected screen... one of "mainmenu", "prefs",
        # "save", "load", or "quit", at least for the default game
        # menu. If None, then it's an indication that none of the
        # nav buttons should be shown.
        def _game_nav(screen, buttons=True):

            ui.add(renpy.Keymap(toggle_fullscreen = renpy.toggle_fullscreen))
            ui.add(renpy.Keymap(game_menu=ui.jumps("_noisy_return")))

            ui.window(style='gm_root_window')
            ui.null()

            if not screen:
                return

            ui.window(style='gm_nav_window')
            ui.vbox(focus='gm_nav')
            
            for key, label, clicked, enabled in library.game_menu:

                disabled = False

                if not eval(enabled):
                    disabled = True
                    clicked = None
                             
                _button_factory(label, "gm_nav",
                                selected=(key==screen),
                                disabled=disabled,
                                clicked=clicked)

            ui.close()

        # This is called from the game menu to interact with the
        # user.  It suppresses all of the underlays and overlays.
        def _game_interact():
            
            return ui.interact(suppress_underlay=True,
                               suppress_overlay=True)

        # This renders an empty slot in the file picker.
        def _render_new_slot(name, save):
            
            if save:
                clicked=ui.returns(("return", (name, False)))
                enable_hover = True
            else:
                clicked = None
                enable_hover = True

            ui.button(style='file_picker_entry',
                      clicked=clicked,
                      enable_hover=enable_hover)
            
            ui.hbox(padding=library.padding)

            if not library.disable_thumbnails:
                ui.null(width=library.thumbnail_width,
                        height=library.thumbnail_height)

            ui.text(name + ". ", style='file_picker_old')
            ui.text(_("Empty Slot."), style='file_picker_empty_slot')
            ui.close()
                      
        # This renders a slot with a file in it, in the file picker.
        def _render_savefile(name, info, newest):

            image, extra = info

            ui.button(style='file_picker_entry',
                      clicked=ui.returns(("return", (name, True))))
            
            ui.hbox(padding=library.padding)

            if not library.disable_thumbnails:
                ui.add(image)
            
            if name == newest:
                ui.text(name + ". ", style='file_picker_new')
            else:
                ui.text(name + ". ", style='file_picker_old')

            
            ui.text(extra, style='file_picker_extra_info')

            ui.close()
            
        _scratch.file_picker_index = None

        # This displays a file picker that can chose a save file from
        # the list of save files.
        def _file_picker(selected, save):

            # The number of slots in a page.
            file_page_length = library.file_page_cols * library.file_page_rows

            saves, newest = renpy.saved_games()

            # The index of the first entry in the page.
            fpi = _scratch.file_picker_index

            if fpi is None:
                fpi = 0

                if newest:
                    fpi = (int(newest) - 1) // file_page_length * file_page_length

                if fpi < 0:
                    fpi = 0

                
            while True:

                if fpi < 0:
                    fpi = 0

                _scratch.file_picker_index = fpi

                # Show Navigation
                _game_nav(selected)
                
                ui.window(style='file_picker_window')
                ui.vbox() # whole thing.
                
                if not library.disable_file_pager:

                    # Draw the navigation.
                    ui.hbox(padding=library.padding * 10, style='file_picker_navbox') # nav buttons.

                    def tb(cond, label, clicked):
                        _button_factory(label, "file_picker_nav", disabled=not cond, clicked=clicked)

                    # Previous
                    tb(fpi > 0, _('Previous'), ui.returns(("fpidelta", -1)))

                    # Quick Access
                    for i in range(0, library.file_quick_access_pages):
                        target = i * file_page_length
                        tb(fpi != target, str(i + 1), ui.returns(("fpiset", target)))

                    # Next
                    tb(True, _('Next'), ui.returns(("fpidelta", +1)))

                    # Done with nav buttons.
                    ui.close()

                # This draws a single slot.
                def entry(offset):
                    i = fpi + offset

                    name = str(i + 1)

                    if name not in saves:
                        _render_new_slot(name, save)
                    else:
                        _render_savefile(name, saves[name], newest)
                    
                # Actually draw a slot.
                ui.grid(library.file_page_cols,
                        library.file_page_rows,
                        style='file_picker_grid',
                        transpose=True) # slots

                for i in range(0, file_page_length):
                    entry(i)

                ui.close() # slots

                ui.close() # whole thing

                result = _game_interact()
                type, value = result

                if type == "return":
                    return value

                if type == "fpidelta":
                    fpi += value * file_page_length

                if type == "fpiset":
                    fpi = value


        # This renders a yes/no prompt, as part of the game menu. If
        # screen is None, then it omits the game menu navigation. 
        def _yesno_prompt(screen, message, nav=True):

            _game_nav(screen)

            ui.window(style='yesno_window')
            ui.vbox(library.padding * 10, xpos=0.5, xanchor='center', ypos=0.5, yanchor='center')

            _label_factory(message, "yesno", xpos=0.5, xanchor='center')

            ui.grid(5, 1, xfill=True)

            # The extra nulls are because we want equal whitespace surrounding
            # the two buttons. It should work as long as we have xfill=True
            ui.null()
            _button_factory("Yes", 'yesno', clicked=ui.returns(True), xpos=0.5, xanchor='center')
            ui.null()
            _button_factory("No", 'yesno', clicked=ui.returns(False), xpos=0.5, xanchor='center')
            ui.null()

            ui.close()
            ui.close()

            return _game_interact()

        def _show_exception(title, message):
            ui.window(style='error_window')
            ui.vbox()

            ui.text(title, style='error_title')
            ui.text("")
            ui.text(message, style='error_body')
            ui.text("")
            ui.text(_("Please click to continue."), style='error_body')

            ui.close()

            ui.saybehavior()

            ui.interact()

        def _quit_prompt(screen="quit"):

            def prompt():
               return _yesno_prompt(screen, "Are you sure you want to quit the game?")
            
            if renpy.invoke_in_new_context(prompt):
                renpy.quit()
            else:
                return

        def _mainmenu_prompt(screen="mainmenu"):

            def prompt():
               return _yesno_prompt(screen, "Are you sure you want to return to the main menu?\nThis will end your game.")
            
            if renpy.invoke_in_new_context(prompt):
                renpy.full_restart()
            else:
                return


            
##############################################################################
# The actual menus begin around here.

# First up, we have the code that is common to all of the entry points into
# the game.

# This is the code that executes when entering a menu context.
label _enter_menu:
    scene
    $ renpy.movie_stop()
    $ renpy.take_screenshot((library.thumbnail_width, library.thumbnail_height))

    # This may be changed, if we are already in the main menu.
    $ renpy.context().main_menu = False

    return
    
# Factored this all into one place, to make our lives a bit easier.
label _enter_game_menu:
    call _enter_menu

    if library.enter_transition:
        $ renpy.transition(library.enter_transition)

    if renpy.has_label("enter_game_menu"):
        call enter_game_menu

    return

##############################################################################
# Now, we have the actual entry points into the various menu screens.

# Entry points from the game into menu-space.
label _game_menu:
label _game_menu_save:
    call _enter_game_menu
    jump _save_screen

label _game_menu_load:
    call _enter_game_menu
    jump _load_screen

label _game_menu_preferences:
    call _enter_game_menu
    jump _prefs_screen

label _confirm_quit:
    call _enter_menu
    $ _quit_prompt(None)
    return
    

##############################################################################
# Finally, we have the actual menu screens that are shown to the user.

label _load_screen:

    python hide:

        fn, exists = _file_picker("load", False )

        if not renpy.context().main_menu and _load_prompt:
            if _yesno_prompt("load", "Loading a new game will end your current game.\nAre you sure you want to do this?"):
                renpy.load(fn)
        else:                        
            renpy.load(fn)

    jump _load_screen

label _save_screen:
    $ _fn, _exists = _file_picker("save", True)

    if not _exists or _yesno_prompt("save", "Are you sure you want to overwrite your save?"):
        python hide:

            if save_name:
                full_save_name = "\n" + save_name
            else:
                full_save_name = ""

            try:
                renpy.save(_fn, renpy.time.strftime("%b %d, %H:%M") +
                           full_save_name)

            except Exception, e:

                if config.debug:
                    raise
                
                message = ( _("The error message was:\n\n") +
                            e.__class__.__name__  + ": " + unicode(e) + "\n\n" +
                            _("You may want to try saving in a different slot, or playing for a while and trying again later."))

                _show_exception(_("Save Failed."), message)
                
                
    jump _save_screen

label _quit:
    $ renpy.quit()

# Make some noise, then return.
label _noisy_return:
    $ renpy.play(library.exit_sound)

# Return to the game.
label _return:

    if renpy.context().main_menu:
        jump _main_menu

    if library.exit_transition:
        $ renpy.transition(library.exit_transition)

    return
