#!/bin/bash

build_addon_zip() {
	ADDON_NAME=$1
	KODI_VERSION=$2
	ADDON_VERSION=`grep "<addon" $ADDON_NAME/addon.xml|sed -e 's/.*version="//g' -e 's/".*//g'`
	OUTPUT_ZIP_FILE="$KODI_VERSION/$ADDON_NAME/$ADDON_NAME-$ADDON_VERSION.zip"

	mkdir -p $KODI_VERSION/$ADDON_NAME

	echo " * Construyendo $ADDON_NAME ($KODI_VERSION) en $OUTPUT_ZIP_FILE ..."

	if [ -f $OUTPUT_ZIP_FILE ]; then
		rm $OUTPUT_ZIP_FILE
	fi

	if [ -e "$ADDON_NAME/resources/icon.png" ]; then
		cp $ADDON_NAME/resources/icon.png $KODI_VERSION/$ADDON_NAME
	fi

	cp $ADDON_NAME/addon.xml $KODI_VERSION/$ADDON_NAME

	# Changelog no deberia ir ni en changelog.md ni en changelog.txt
	# Si lo pongo en md es para que se visualice chuli con un interprete
	# de md... :P
	CHANGELOG_FILE="$ADDON_NAME/resources/changelog.md"

	if [ -f $ADDON_NAME/resources/changelog.txt ]; then
		CHANGELOG_FILE="$ADDON_NAME/resources/changelog.txt"
	fi

	if [ -f $CHANGELOG_FILE ]; then
		# <news></news> solo admite 1500 caracteres, ponemos 1400 para curarnos 
		# en salud :P
		NEWS_DESCRIPTION=`head -c 1400 $CHANGELOG_FILE`
		ESCAPED_NEWS_DESCRIPTION=$(printf '%s\n' "$NEWS_DESCRIPTION" | sed -e 's/[\/&]/\\&/g' |tr $'\n' "~")
		sed -i "s/news></news>$ESCAPED_NEWS_DESCRIPTION</g" $KODI_VERSION/$ADDON_NAME/addon.xml
		cat $KODI_VERSION/$ADDON_NAME/addon.xml|tr "~" $'\n' > $KODI_VERSION/$ADDON_NAME/addon.xml.tmp
		mv $KODI_VERSION/$ADDON_NAME/addon.xml.tmp $KODI_VERSION/$ADDON_NAME/addon.xml
	fi

	cat $KODI_VERSION/$ADDON_NAME/addon.xml|grep -v "<?xml" >> $KODI_VERSION/addons.xml

	zip -qr $OUTPUT_ZIP_FILE $ADDON_NAME/
	cp $OUTPUT_ZIP_FILE $KODI_VERSION/$ADDON_NAME-latest.zip
}

convert_from_matrix_to_leia() {
	ADDON_NAME=$1

	echo " * Convirtiendo $ADDON_NAME de matrix a leia ..."
	sed -i 's/addon="xbmc.python" version="3.0.0"/addon="xbmc.python" version="2.25.0"/g' $ADDON_NAME/addon.xml
}

# WORKDIR = build/
mkdir -p build

for addon_dir in repository.homodaba plugin.homodaba.movies
do
	rsync -qa --del src/$addon_dir/ build/$addon_dir/
done

cd build

for kodi_version in matrix leia
do
	mkdir -p $kodi_version
	echo "<?xml version='1.0' encoding='UTF-8'?>" > $kodi_version/addons.xml
	echo "<addons>" >> $kodi_version/addons.xml
	build_addon_zip repository.homodaba $kodi_version
	if [ "$kodi_version" == "leia" ]; then
		convert_from_matrix_to_leia plugin.homodaba.movies
	fi
	build_addon_zip plugin.homodaba.movies $kodi_version
	echo "</addons>" >> $kodi_version/addons.xml
	md5sum $kodi_version/addons.xml | sed -e "s/ .*//g"> $kodi_version/addons.xml.md5

	rsync -va $kodi_version/ ../$kodi_version/
done

for addon_dir in repository.homodaba plugin.homodaba.movies
do
	rm -rf $addon_dir
done

# VOLVEMOS AL RAIZ
cd ..

echo "Para no cambiar zips del repo innecesariamente, casi seguro que vas a querer hacer esto:"
echo ""
echo "git restore leia/repository.homodaba-latest.zip"
echo "git restore leia/repository.homodaba/repository.homodaba-1.0.0.zip"
echo "git restore matrix/repository.homodaba-latest.zip"
echo "git restore matrix/repository.homodaba/repository.homodaba-1.0.0.zip"
echo ""
echo "Los cambios que hay actualmente en el repo son:"
git status