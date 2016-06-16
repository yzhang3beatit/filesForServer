set nocompatible
syntax on
set noeb
set confirm
set autoindent
set cindent
set tabstop=4
set softtabstop=4
set shiftwidth=4
set expandtab
set smarttab
set number
set history=1000
set nobackup
set noswapfile
set ignorecase
set hlsearch
set incsearch
set gdefault
set enc=utf-8
set fencs=utf-8,ucs-bom,shift-jis,gb18030,gbk,gb2312,cp936
set langmenu=zh_CN.UTF-8
set helplang=cn

set statusline=%F%m%r%h%w\ [FORMAT=%{&ff}]\ [TYPE=%Y]\ [POS=%l,%v][%p%%]\ %{strftime(\"%d/%m/%y\ -\ %H:%M\")}
"set statusline=[%F]%y%r%m%*%=[Line:%l/%L,Column:%c][%p%%]
"colors morning
colors desert
set laststatus=2
set ruler           
set cmdheight=2
filetype on
filetype plugin on
filetype indent on

set viminfo+=!
set iskeyword+=_,$,@,%,#,-
set linespace=0
set wildmenu
set backspace=2
set whichwrap+=<,>,h,l

"set mouse=a
set selection=exclusive
set selectmode=mouse,key

set report=0
set shortmess=atI
set fillchars=vert:\ ,stl:\ ,stlnc:\
set showmatch
set matchtime=5
set scrolloff=3
set smartindent
if has("autocmd")
   autocmd FileType xml,html,c,cs,java,perl,shell,bash,cpp,python,vim,php,ruby set number
   autocmd FileType xml,html vmap <C-o> <ESC>'<i<!--<ESC>o<ESC>'>o-->
   autocmd FileType java,c,cpp,cs vmap <C-o> <ESC>'<o/*<ESC>'>o*/
   autocmd FileType html,text,php,vim,c,java,xml,bash,shell,perl,python setlocal textwidth=100
   autocmd Filetype html,xml,xsl source $VIMRUNTIME/plugin/closetag.vim
   autocmd BufReadPost *
      \ if line("'\"") > 0 && line("'\"") <= line("$") |
      \   exe "normal g`\"" |
      \ endif
endif " has("autocmd")

map <F5> :call CompileRunGcc()<CR>
func! CompileRunGcc()
exec "w"
exec "!gcc % -o %<"
exec "! ./%<"
endfunc

map <F6> :call CompileRunGpp()<CR>
func! CompileRunGpp()
exec "w"
exec "!g++ % -o %<"
exec "! ./%<"
endfunc

set encoding=utf-8
function! SetFileEncodings(encodings)
    let b:myfileencodingsbak=&fileencodings
    let &fileencodings=a:encodings
endfunction
function! RestoreFileEncodings()
    let &fileencodings=b:myfileencodingsbak
    unlet b:myfileencodingsbak
endfunction

au BufReadPre *.nfo call SetFileEncodings('cp437')|set ambiwidth=single
au BufReadPost *.nfo call RestoreFileEncodings()

au BufRead,BufNewFile *  setfiletype txt

"set foldenable
"set foldmethod=manual
nnoremap <space> @=((foldclosed(line('.')) < 0) ? 'zc' : 'zo')<CR>

let g:miniBufExplMapWindowNavVim = 1
let g:miniBufExplMapWindowNavArrows = 1
let g:miniBufExplMapCTabSwitchBufs = 1
let g:miniBufExplModSelTarget = 1  

let g:NERDTreeWinSize=20
let g:NERDTreeChDirMode=2
let g:NERDTreeIgnore=['\.svn$', '\~$', '\.git$']

"F7 NERDTree
map <F7> :NERDTreeToggle<CR>
imap <F7> <ESC>:NERDTreeToggle<CR>

"F8 TlistToggle
map <F10> :TlistToggle<CR>
imap <F10> <ESC>:TlistToggle<CR>

"F9 SrcExpl
map <F9> :SrcExplToggle<CR>
imap <F9> <ESC>:ScrExplToggle<CR>

let Tlist_Ctags_Cmd="ctags-exuberant"
let Tlist_Auto_Open=1
let Tlist_Inc_Winwidth=0
let Tlist_Use_Right_Window=1
let Tlist_File_Fold_Auto_Close=1 
let Tlist_Process_File_Always=1
let Tlist_Sort_Type="name"
let Tlist_WinWidth=25

" // Set the height of Source Explorer window"
let g:SrcExpl_winHeight = 8
" // Set 100 ms for refreshing the Source Explorer"
let g:SrcExpl_refreshTime = 100
" // Set "Enter" key to jump into the exact definition context"
"let g:SrcExpl_jumpKey = "<ENTER>"
"// Set "Space" key for back from the definition context "
"let g:SrcExpl_gobackKey = "<SPACE>"
" // In order to avoid conflicts, the Source Explorer should know what plugins except itself are using buffers. And you need add their buffer names into below listaccording to the command :buffers!"                 
let g:SrcExpl_pluginList = [
      \ "__Tag_List__",
      \ "_NERD_tree_"
    \ ]
"// Enable/Disable the local definition searching, and note that this is not
"// guaranteed to work, the Source Explorer doesn't check the syntax for now. "
"// It only searches for a match with the keyword according to command 'gd'   "
let g:SrcExpl_searchLocalDef = 1                                                           "
" // Do not let the Source Explorer update the tags file when opening  "
let g:SrcExpl_isUpdateTags = 0
"// Use 'Exuberant Ctags' with '--sort=foldcase -R .' or '-L cscope.files' to "
"//  create/update a tags file                                                "
let g:SrcExpl_updateTagsCmd = "ctags-exuberant --sort=foldcase -R ."
                                                                              "
" Set "<F12>" key for updating the tags file artificially                   "
let g:SrcExpl_updateTagsKey = "<F12>"
                                                                              "
"// Set "<F3>" key for displaying the previous definition in the jump list    "
let g:SrcExpl_prevDefKey = "<F3>"
                                                                              "
"// Set "<F4>" key for displaying the next definition in the jump list        "
let g:SrcExpl_nextDefKey = "<F4>" 
