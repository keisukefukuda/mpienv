#!/bin/sh

mkdir -p $HOME/mpi
mkdir -p $HOME/tmp


# Install zsh
if [ ! -x $HOME/zsh/bin/zsh ]; then
    rm -f zsh-5.3.1.tar.gz
    rm -rf zsh  # clear zsh/ directory
    
    mkdir $HOME/zsh
    wget --no-check-certificate 'https://downloads.sourceforge.net/project/zsh/zsh/5.3.1/zsh-5.3.1.tar.gz?r=http%3A%2F%2Fzsh.sourceforge.net%2FArc%2Fsource.html&ts=1495843150&use_mirror=jaist' -O zsh-5.3.1.tar.gz

    tar -xf zsh-5.3.1.tar.gz
    cd zsh-5.3.1
    echo configure
    ./configure --prefix=$HOME/zsh >/dev/null 2>&1
    echo make
    make -j2  >/dev/null 2>&1
    echo make install
    make install >/dev/null 2>&1
    cd
else
    echo zsh is ready
    $HOME/zsh/bin/zsh --version
fi

