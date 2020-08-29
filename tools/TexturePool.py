import ctypes
import math

from dataclasses import dataclass, field
from typing import Callable, Mapping, Tuple, Optional

from panda3d import core as p3d

from direct.directnotify import DirectNotifyGlobal

from .DSOLoader import DSOLoader


LOG = DirectNotifyGlobal.directNotify.newCategory(__name__)
VFS = p3d.VirtualFileSystem.getGlobalPtr()
BAM = p3d.BamCache.getGlobalPtr()


# src/gobj/texture.cxx L:1991-2001
def downToPower(val: int, pow_: int = 2):
    if val < 1:
        return 1
    else:
        return pow(pow_, math.floor(math.log(val) / math.log(pow_)))


# src/gobj/texture.cxx L:1979-1989
def upToPower(val: int, pow_: int = 2):
    if val < 1:
        return 1
    else:
        return pow(pow_, math.ceil(math.log(val) / math.log(pow_)))


# src/gobj/texturePool.h L:152-160
@dataclass(eq=True, frozen=True)
class _CacheKey:
    f_name: p3d.Filename
    alpha_f_name: p3d.Filename


# src/gobj/texture.cxx L:10431-10479
@dataclass(eq=True, frozen=True)
class _CacheVal:
    texture: p3d.Texture
    primary_file_num_channels: int = 0
    alpha_file_channel: int = 0
    type_: int = p3d.Texture.TT2dTexture


class TexturePool(object):
    """
    /**
     * This is the preferred interface for loading textures from image files.
     * It unifies all references to the same filename, so that multiple
     * models that reference the same textures don't waste texture memory.
     */
    """

    BAM_TYPES = ('txo', 'bam')
    TEX_TYPES = ('txo', 'dds', 'ktx')

    TP_Options = p3d.LoaderOptions()
    CM_Options = {
        # src/putil/bamCache.cxx L:67-70
        'active': ('model-cache-textures', True),
        # src/putil/bamCache.cxx L:72-77
        'compress_cache': ('model-cache-compressed-textures', False),
        # src/gobj/config_gobj.cxx L:123-134
        'driver_compress': ('driver-compress-textures', False),
        # src/gobj/config_gobj.cxx L:136-140
        'driver_mipmaps': ('driver-generate-mipmaps', True),
        # src/gobj/config_gobj.cxx L:328-333
        'header_only': ('textures-header-only', False),
        # src/putil/config_putil.cxx L:157-162
        'compress': ('compressed-textures', False),
    }

    _NULL_NAME = p3d.Filename()

    @staticmethod
    def isCompressed(tex: p3d.Texture) -> bool:
        return (tex.getRamImageCompression() != p3d.Texture.CMOff)

    # src/putil/autoTextureScale.cxx L:44-73
    @staticmethod
    def getAutoTextureScale(word: str) -> int:
        # src/putil/autoTextureScale.cxx L:44-73
        word = word.lower().strip()
        # src/putil/autoTextureScale.cxx L:49-53
        if (word in ('none', '0', '#f')) or word.startswith('f'):
            # src/putil/autoTextureScale.cxx L:53
            return p3d.ATSNone
        # src/putil/autoTextureScale.cxx L:55-59
        elif (word in ('down', '1', '#t')) or word.startswith('t'):
            return p3d.ATSDown
        # src/putil/autoTextureScale.cxx L:61-62
        elif textures_square == 'up':
            return p3d.ATSUp
        # src/putil/autoTextureScale.cxx L:64-65
        elif textures_square == 'pad':
            return p3d.ATSPad
        # src/putil/autoTextureScale.cxx L:67-70
        else:
            LOG.warning(f'invalid AutoTextureScale value: {textures_square}')
            return p3d.ATSNone

    def __init__(self):
        # src/gobj/texturePool.h L:161-164
        self._textures: Mapping[self.CacheKey, self.CacheTex] = {}
        self._relpath_lookup: Mapping[p3d.Filename, p3d.Filename] = {}

        # src/gobj/texturePool.h L:171-175
        self._type_registry: Mapping[str, Callable] = {}
        self._filter_registry: List[p3d.TexturePoolFilter] = []
        # src/gobj/texturePool.cxx L:152
        self._loadFilters()

        # src/gobj/texturePool.cxx L:157-171
        self._fake_image = p3d.ConfigVariable('fake-texture-image')
        self._fake_image = p3d.Filename(self._fake_image.getStringValue())

        # Convenience load all ConfigVariables at init
        for key, (option, default) in self.CM_Options.items():
            key = key.replace('_', ' ').title()
            key = 'CM_' + key.replace(' ', '')
            val = p3d.ConfigVariableBool(option, default).getValue()
            setattr(self, key, val)

    # src/gobj/texturePool.cxx L:1023-1051
    def _resolveFilename(self,
                         f_path: p3d.Filename,
                         read_mipmaps: bool,
                         options: p3d.LoaderOptions) -> p3d.Filename:
        """
        /**
         * Searches for the indicated filename along the model path.
         * If the filename was previously searched for, doesn't search again,
         * as an optimization. Assumes _lock is held.
         */
        """
        if f_path:
            if f_path not in self._relpath_lookup:
                abs_path = p3d.Filename(f_path)
                # texturePool.cxx L:1042-1045
                if read_mipmaps or (options.getTextureFlags() \
                                    & p3d.LoaderOptions.TFMultiview):
                    abs_path.setPattern(True)
                # texturePool.cxx L:1047-1050
                search_path = p3d.getModelPath().getValue()
                VFS.resolveFilename(abs_path, search_path)
                self._relpath_lookup[f_path] = abs_path
            # texturePool.cxx L:1036-1040
            return self._relpath_lookup[f_path]
        else:
            return self._NULL_NAME

    # src/gobj/texturePool.cxx L:46-63
    def _registerTextureType(self, func: Callable, exts: str) -> None:
        """
        /**
         * Records a factory function that makes a Texture object of the
         * appropriate type for one or more particular filename extensions.
         * The string extensions may be a string that contains space-separated
         * list of extensions, case-insensitive.
         */
        """
        for ext in exts.lower().split():
            self._type_registry[ext] = func

    # src/gobj/texturePool.cxx L:78-105
    def _getTextureType(self,
                        ext: str, default: Callable) -> Optional[Callable]:
        """
        /**
         * Returns the factory function to construct a new texture of the type
         * appropriate for the indicated filename extension, if any, or NULL
         * if the extension is not one of the extensions for a texture file.
         */
        """
        if ext:
            # src/gobj/texturePool.cxx L:87
            ext = ext.lower()
            if ext not in self._type_registry:
                # src/gobj/texturePool.cxx L:94-101
                pnm = p3d.PNMFileTypeRegistry.getGlobalPtr()
                type_ = pnm.getTypeFromExtension(ext)
                if type_ or (ext in self.TEX_TYPES):
                    # // This is a known image type; create an ordinary Texture.
                    self._type_registry[ext] = default
                else:
                    # // This is an unknown texture type.
                    return None
        # src/gobj/texturePool.cxx L:88-92
        return self._type_registry.get(ext, default)

    # src/gobj/texturePool.cxx L:65-76
    def _registerFilter(self, filter) -> None:
        """
        /**
         * Records a TexturePoolFilter object that may operate on texture
         * images as they are loaded from disk.
         */
        """
        LOG.info(f'registering texture filter: {filter}')
        self._filter_registry.append(filter)

    # src/gobj/texturePool.cxx L:1253-1278
    def _loadFilters(self) -> None:
        """
        /**
         * Loads up all of the dll's named by the texture-filter
         * Config.prc variable.
         */
        """
        # src/gobj/texturePool.cxx L:1258-1263
        filters = p3d.ConfigVariableList('texture-filter')
        # src/gobj/texturePool.cxx L:1265-1277
        for filter_n in range(filters.getNumUniqueValues()):
            # src/gobj/texturePool.cxx L:1269-1271
            f_name = p3d.Filename.dsoFilename(filters.getUniqueValue(filter_n))
            LOG.info(f'loading texture filter: {f_name.toOsSpecific()}')
            # src/gobj/texturePool.cxx L:1272-1276
            search_path = p3d.getPluginPath().getValue()
            dso = DSOLoader(search_path, f_name)
            if not dso.load():
                msg = dso.getErrorMsg(dso.getErrorCode())
                LOG.error(f'unable to load: {msg}')

    # src/gobj/texturePool.cxx L:1161-1203
    def _report(self, f_name: p3d.Filename) -> None:
        """
        /**
         * Prints a suitable error message when a texture could not be loaded.
         */
        """
        # src/gobj/texturePool.cxx L:1167
        has_hash = f_name.getFullpath().endswith('#')
        # src/gobj/texturePool.cxx L:1168-1180
        if not has_hash and not VFS.exists(f_name):
            # src/gobj/texturePool.cxx L:1169-1174
            if f_name.isLocal():
                # // The file doesn't exist, and it wasn't fully-qualified --
                # // therefore, it wasn't found along either search path.
                path = p3d.getModelPath().getValue()
                LOG.error(f'unable to find texture: {f_name}; path: {path}')
            # src/gobj/texturePool.cxx L:1175-1180
            else:
                # // A fully-specified filename is not searched along the path,
                # // so don't mislead the user with the error message.
                LOG.error(f'texture does not exist: {f_name}')
        # src/gobj/texturePool.cxx L:1182-1202
        else:
            # src/gobj/texturePool.cxx L:1183-1186
            # // The file exists, but it couldn't be read for some reason.
            if not has_hash:
                LOG.error(f'texture exists but cannot be read: {f_name}')
            # src/gobj/texturePool.cxx L:1187-1192
            else:
                # // If the filename contains a hash, we'll be noncommittal
                # // about whether it exists or not.
                LOG.error(f'texture cannot be read: {f_name}')

    # src/gobj/texturePool.cxx L:1205-1231
    def _preLoad(self,
                 f_name: p3d.Filename, alpha_f_name: p3d.Filename,
                 primary_file_num_channels: int, alpha_file_channel: int,
                 read_mipmaps: bool,
                 options: p3d.LoaderOptions) -> Optional[p3d.Texture]:
        """
        /**
         * Invokes pre_load() on all registered filters until one returns
         * non-None; returns None if there are no registered filters or if
         * all registered filters returned None.
         */
        """
        # src/gobj/texturePool.cxx L:1218-1228
        for filter_ in self._filter_registry:
            tex = filter_.pre_load(f_name, alpha_f_name,
                                   primary_file_num_channels,
                                   alpha_file_channel,
                                   read_mipmaps, options)
            if tex:
                return tex
            else:
                # src/gobj/texturePoolFilter.cxx L:25-36
                return None
        else:
            return None

    # src/gobj/texturePool.cxx L:1233-1250
    def _postLoad(self, tex: p3d.Texture) -> p3d.Texture:
        """
        /**
         * Invokes post_load() on all registered filters.
         */
        """
        # src/gobj/texturePool.cxx L:1242-1247
        for filter_ in self._filter_registry:
            result = filter_.post_load(tex)
            if result:
                return result
            else:
                # src/gobj/texturePoolFilter.cxx L:38-48
                return tex
        else:
            return tex

    # src/gobj/texturePool.cxx L:1053-1159
    def _tryLoadCache(self,
                      f_path: p3d.Filename, options: p3d.LoaderOptions
                      ) -> Tuple[Optional[p3d.BamCacheRecord],
                                 Optional[p3d.Texture],
                                 bool]:
        """
        /**
         * Attempts to load the texture from the cache record.
         */
        """
        tex = record = None
        compressed = False
        # src/gobj/texturePool.cxx L:1063
        if not self.CM_HeaderOnly \
           and (self.CM_Active or self.CM_CompressCache):
            # src/gobj/texturePool.cxx L:1069-1072
            dummy = self.makeTexture(f_path.getExtension())
            dummy.clear()
            # src/gobj/texturePool.cxx L:1074-1156
            record = BAM.lookup(f_path, self.BAM_TYPES[0])
            if record:
                # src/gobj/texturePool.cxx L:1076-1144
                if record.hasData():
                    # src/gobj/texturePool.cxx L:1077-1080
                    tex = record.getData()
                    # src/gobj/texturePool.cxx L:1078
                    compressed = self.isCompressed(tex)

                    # src/gobj/texturePool.cxx L:1079-1080
                    x_size = tex.getOrigFileXSize()
                    y_size = tex.getOrigFileYSize()
                    # src/gobj/texturePool.cxx L:1081
                    x_size, y_size = self._adjustSize(
                        x_size, y_size,
                        f_path.getBasename(), True,
                        options.getAutoTextureScale())

                    # src/gobj/texturePool.cxx L:1083-1090
                    if not self.CM_Active and not compressed:
                        # // We're not supposed to cache uncompressed textures.
                        LOG.debug(f'not caching uncompressed texture: '
                                  f'{f_path}')
                        tex = None
                    # src/gobj/texturePool.cxx L:1092-1105
                    elif x_size != tex.getXSize() or y_size != tex.getYSize():
                        # // The cached texture no longer matches our expected
                        # // size (the resizing config variables must have
                        # // changed). We'll have to reload the texture from
                        # // its original file so we can rebuild the cache.
                        LOG.debug(f'wrong size; dropping cache: {f_path}')
                        tex = None
                    # src/gobj/texturePool.cxx L:1107-1114
                    elif not self.CM_CompressCache and compressed:
                        # // This texture shouldn't be compressed,
                        # // but it is. Go reload it.
                        LOG.debug(f'compressed in cache; '
                                  f'dropping cache: {f_path}')
                        tex = None
                    # src/gobj/texturePool.cxx L:1116-1143
                    else:
                        LOG.info(f'found in disk cache: {f_path}')

                        # src/gobj/texturePool.cxx L:1119-1122
                        if not tex.hasSimpleRamImage() \
                           and (options.getTextureFlags()
                                & p3d.LoaderOptions.TFPreloadSimple):
                            tex.generateSimpleRamImage()

                        # src/gobj/texturePool.cxx L:1123-1127
                        if not (options.getTextureFlags()
                                & p3d.LoaderOptions.TFPreload):
                            # // But drop the RAM until we need it.
                            tex.clearRamImage()
                        # src/gobj/texturePool.cxx L:1127-1140
                        else:
                            # src/gobj/texturePool.cxx L:1128
                            was_compressed = self.isCompressed(tex)
                            # src/gobj/texturePool.cxx L:1129-1140
                            if self._considerAutoProcessRamImage(tex, True):
                                # src/gobj/texturePool.cxx L:1131-1139
                                if not was_compressed \
                                   and self.isCompressed(tex) \
                                   and self.CM_CompressCache:
                                    # // We've re-compressed the image after
                                    # // loading it from the cache.  To keep
                                    # // the cache current, rewrite it to the
                                    # // cache now, in newly compressed form.
                                    LOG.debug(f'storing compressed texture: '
                                              f'{f_path}')
                                    record.setData(tex)
                                    BAM.store(record)
                                    compressed = True
                        # src/gobj/texturePool.cxx L:1142
                        tex.setKeepRamImage(False)
                # src/gobj/texturePool.cxx L:1144-1155
                else:
                    if not self.CM_Active:
                        # // This texture has no actual record, and therefore
                        # // no compressed record (yet).  And we're not
                        # // supposed to be caching uncompressed textures.
                        LOG.info('not caching uncompressed texture')
                        record = None

        return (record, tex, compressed)

    # src/gobj/texture.cxx L:2762-2771;2630-2734
    def _adjustSize(self,
                    x_size: int, y_size: int, name: str,
                    for_padding: bool, auto_texture_scale: int
                    ) -> Tuple[int, int]:
        """
        /**
         * Computes the proper size of the texture, based on the original size,
         * the filename, and the resizing whims of the config file.
         *
         * x_size and y_size should be loaded with the texture image's original
         * size on disk.  On return, they will be loaded with the texture's
         * in-memory target size.  The return value is true if the size has
         * been adjusted, or false if it is the same.
         */
        """
        exclude = False
        # src/gobj/config_gobj.cxx L:106-112
        excludes = p3d.ConfigVariableList('exclude-texture-scale')
        # src/gobj/texture.cxx L:2643-2649
        for exclude_n in range(excludes.getNumUniqueValues()):
            pattern = p3d.GlobPattern(excludes.getUniqueValue(exclude_n))
            if pattern.matches(name):
                exclude = True

        # src/gobj/texture.cxx L:2654-2662
        if not exclude:
            # src/gobj/config_gobj.cxx L:92-98
            scale = p3d.ConfigVariableDouble('texture-scale').getValue()
            # src/gobj/config_gobj.cxx L:100-104
            max_limit = p3d.ConfigVariableInt('texture-scale-limit').getValue()
            # src/gobj/texture.cxx L:2655-2656
            new_x_size = math.floor(x_size * scale + 0.5)
            new_y_size = math.floor(y_size * scale + 0.5)
            # src/gobj/texture.cxx L:2658-2661
            # // Don't auto-scale below 4 in either dimension.
            # // This causes problems for DirectX and texture compression.
            new_x_size = min(max(x_size, max_limit), x_size)
            new_y_size = min(max(y_size, max_limit), y_size)
        # src/gobj/texture.cxx L:2651-2652
        else:
            new_x_size = x_size
            new_y_size = y_size

        # src/gobj/texture.cxx L:2664-2667
        if auto_texture_scale == p3d.ATSUnspecified:
            # src/gobj/texture.I L:1856-1869
            # src/gobj/config_gobj.cxx L:304-311
            power_2 = p3d.ConfigVariable('textures-power-2').getStringValue()
            auto_texture_scale = self.getAutoTextureScale(power_2)

        # src/gobj/texture.cxx L:2668-2673
        if not for_padding and (auto_texture_scale == p3d.ATSPad):
            # // If we're not calculating the padding size--that is, we're
            # // calculating the initial scaling size instead--then ignore
            # // ATS_pad, and treat it the same as ATS_none.
            auto_texture_scale = p3d.ATSNone

        # src/gobj/texture.cxx L:2675-2690
        if auto_texture_scale == p3d.ATSDown:
            new_x_size = downToPower(x_size)
            new_y_size = downToPower(y_size)
        # src/gobj/texture.cxx L:2681-2685
        elif auto_texture_scale in (p3d.ATSUp, p3d.ATSPad):
            new_x_size = upToPower(x_size)
            new_y_size = upToPower(y_size)
        # src/gobj/texture.cxx L:2687-2689
        else:
            pass

        # src/gobj/texture.cxx L:2692
        # src/gobj/config_gobj.cxx L:313-317
        square = p3d.ConfigVariable('textures-square').getStringValue()
        auto_texture_scale = self.getAutoTextureScale(square)

        # src/gobj/texture.cxx L:2692-2695
        if not for_padding and (auto_texture_scale == p3d.ATSPad):
            auto_texture_scale = p3d.ATSNone

        # src/gobj/texture.cxx L:2697-2699
        if auto_texture_scale == p3d.ATSDown:
            new_x_size = new_y_size = min(new_x_size, new_y_size)
        # src/gobj/texture.cxx L:2701-2704
        elif auto_texture_scale in (p3d.ATSUp, p3d.ATSPad):
            new_x_size = new_y_size = max(new_x_size, new_y_size)
        # src/gobj/texture.cxx L:2706-2709
        else:
            pass

        # src/gobj/texture.cxx L:2711-2725
        if not exclude:
            # src/gobj/texture.cxx L:2712
            # src/gobj/config_gobj.cxx L:81-90
            max_dim = p3d.ConfigVariableInt('max-texture-dimension').getValue()

            # src/gobj/texture.cxx L:2714-2719
            if max_dim < 0:
                gsg = p3d.GraphicsStateGuardianBase.getDefaultGsg()
                if gsg:
                    max_dim = gsg.getMaxTextureDimension()

            # src/gobj/texture.cxx L:2721-2724
            if max_dim > 0:
                new_x_size = min(new_x_size, max_dim)
                new_y_size = min(new_y_size, max_dim)

        # src/gobj/texture.cxx L:2727-2731
        if (x_size != new_x_size) or (y_size != new_y_size):
            return (new_x_size, new_y_size)
        # src/gobj/texture.cxx L:2733
        else:
            return (x_size, y_size)

    # src/gobj/texture.cxx L:5720-5757
    def _considerAutoProcessRamImage(self,
                                     tex: p3d.Texture, compress: bool) -> bool:
        """
        /**
         * Should be called after a texture has been loaded into RAM,
         * this considers generating mipmaps and/or compressing the RAM image.
         *
         * Returns true if the image was modified by this operation, false
         * if it wasn't.
         */
        """
        # src/gobj/texture.cxx L:5730
        modified = False

        # src/gobj/texture.cxx L:5732-5736
        if tex.uses_mipmaps and not self.CM_DriverMipmaps \
           and tex.hasRamImage():
            # src/gobj/texture.cxx L:5734-5735
            tex.generateRamMipmapImages()
            modified = True

        # src/gobj/texture.cxx L:5738-5754
        if compress and not self.CM_DriverCompress:
            # src/gobj/texture.cxx L:5739
            compression = tex.getCompression()

            # src/gobj/texture.cxx L:5740-5742
            if (compression == p3d.Texture.CMDefault) and self.CM_Compress:
                # src/gobj/texture.cxx L:5741
                compression = p3d.Texture.CMOn

            # src/gobj/texture.cxx L:5743-5753
            if (compression > p3d.Texture.CMOff) \
               and not self.isCompressed(tex):
                # src/gobj/texture.cxx L:5744
                gsg = p3d.GraphicsStateGuardianBase.getDefaultGsg()
                # src/gobj/texture.cxx L:5745-5752
                if tex.compressRamImage(compression,
                                        p3d.Texture.QLDefault,
                                        gsg):
                    # src/gobj/texture.cxx L:5746-5751
                    LOG.debug(f'compressed; '
                              f'mode: {tex.getRamImageCompression()}')
                    modified = True
            else:
                if self.isCompressed(tex):
                    LOG.debug('already compressed')

        # src/gobj/texture.cxx L:5756
        return modified

    # src/gobj/texturePool.I L:180-187
    def rehash(self) -> None:
        """
        /**
         * Should be called when the model-path changes, to blow away the
         * cache of texture pathnames found along the model-path.
         */
        """
        self._relpath_lookup.clear()

    # src/gobj/texturePool.I L:269-277
    # src/gobj/texturePool.cxx L:1006-1021
    def makeTexture(self,
                    ext: str, default: Optional[Callable] = p3d.Texture
                    ) -> Optional[p3d.Texture]:
        """
        /**
         * Creates a new Texture object of the appropriate type for the
         * indicated filename extension, according to the types that have
         * been registered via register_texture_type().
         */
        """
        # src/gobj/texturePool.cxx L:1013-L1016
        func = self._getTextureType(ext, p3d.Texture)
        if func:
            return func()
        else:
            return None

    # src/gobj/texturePool.I L:16-22
    # src/gobj/texturePool.cxx L:173-195
    def hasTexture(self, f_name: p3d.Filename) -> bool:
        """
        /**
         * Returns true if the texture has ever been loaded, false otherwise.
         */
        """
        # src/gobj/texturePool.cxx L:180-181
        key = _CacheKey(
            self._resolveFilename(f_name, False, self.TP_Options),
            self._resolveFilename(None, False, self.TP_Options))

        # src/gobj/texturePool.cxx L:183-188
        if key in self._textures:
            return True
        else:
            # src/gobj/texturePool.cxx L:190-195
            for k in self._textures:
                if key.f_name == k.f_name:
                    return True
            # src/gobj/texturePool.cxx L:197
            else:
                return False

    # src/gobj/texturePool.cxx L:852-866
    def releaseTexture(self, tex: p3d.Texture) -> None:
        """
        /**
         * Removes the indicated texture from the pool, indicating it will
         * never be loaded again; the texture may then be freed. If this
         * function is never called, a reference count will be maintained on
         * every texture ever loaded, and textures will never be freed.
         *
         * The texture's name should not have been changed during its
         * lifetime, or this function may fail to locate it in the pool.
         */
        """
        # src/gobj/texturePool.cxx L:859-866
        for key, val in self._textures.items():
            if val == tex:
                del self._textures[key]
                break
        # src/gobj/texturePool.cxx L:859-866
        else:
            # // Blow away the cache of resolved relative filenames.
            self.rehash()

    # src/gobj/texturePool.cxx L:872-890
    def releaseAllTextures(self) -> None:
        """
        /**
         * Releases all textures in the pool and restores the pool to
         * the empty state.
         */
        """
        self._textures.clear()
        self._relpath_lookup.clear()

    # src/gobj/texturePool.cxx L:823-850
    def addTexture(self, tex: p3d.Texture) -> None:
        """
        /**
         * Adds the indicated already-loaded texture to the pool. The texture
         * must have a filename set for its name. The texture will always
         * replace any previously-loaded texture in the pool that had the
         * same filename.
         */
        """
        # src/gobj/texturePool.cxx L:831-833
        if tex.getFullpath() in self._relpath_lookup.values():
            self.releaseTexture(tex)

        # src/gobj/texturePool.cxx L:835-839
        if tex.getFullpath().empty():
            LOG.error('attempt to call addTexture on an unnamed texture')
        # src/gobj/texturePool.cxx L:841-849
        else:
            key = _CacheKey(tex.getFullpath(), tex.getAlphaFilename())
            val = _CacheVal(tex, type_=tex.getTextureType())
            # // We blow away whatever texture was there previously, if any.
            self._textures[key] = val

    def findTexture(self, name: str) -> Optional[p3d.Texture]:
        """
        /**
         * Returns the first texture found in the pool that matches the
         * indicated name (which may contain wildcards). Returns the texture
         * if it is found, or NULL if it is not.
         */
        """
        # src/gobj/texturePool.cxx L:973
        pattern = p3d.GlobPattern(name)
        # src/gobj/texturePool.cxx L:976-981
        for val in self._textures.values():
            if pattern.matches(val.texture.getName()):
                return val.texture
        # src/gobj/texturePool.cxx L:983
        else:
            return None

    def findAllTextures(self, name: str) -> p3d.TextureCollection:
        """
        /**
         * Returns the set of all textures found in the pool that match
         * the indicated name (which may contain wildcards).
         */
        """
        # src/gobj/texturePool.cxx L:992
        results = p3d.TextureCollection()
        # src/gobj/texturePool.cxx L:993
        pattern = p3d.GlobPattern(name)
        # src/gobj/texturePool.cxx L:996-1001
        for val in self._textures.values():
            if pattern.matches(val.texture.getName()):
                results.addTexture(val.texture)
        # src/gobj/texturePool.cxx L:1003
        return results

    # src/gobj/texturePool.I L:53-71
    # src/gobj/texturePool.cxx L:354-482
    def loadTexture(self,
                    f_name: p3d.Filename,
                    alpha_f_name: Optional[p3d.Filename] = None,
                    primary_file_num_channels: int = 0,
                    alpha_file_channel: int = 0,
                    read_mipmaps: bool = False,
                    options: p3d.LoaderOptions = TP_Options
                    ) -> Optional[p3d.Texture]:
        """
        /**
         * Loads the given filename up into a texture, if it has not already
         * been loaded, and returns the new texture. If a texture with the
         * same filename was previously loaded, returns that one instead.
         * If the texture file cannot be found, returns NULL.
         *
         * If read_mipmaps is true, the filename should contain a hash
         * mark ('#'), which will be filled in with the mipmap level number;
         * and the texture will be defined with a series of images, one for
         * each mipmap level.
         */
        """
        # Safe init default alpha_f_name
        if not alpha_f_name:
            alpha_f_name = self._NULL_NAME

        # Verify Filename types
        if not isinstance(f_name, p3d.Filename):
            LOG.warning('loadTexture: f_name must be of type Filename')
            return None
        elif not isinstance(alpha_f_name, p3d.Filename):
            LOG.warning('loadTexture: alpha_f_name must be of type Filename')
            return None
        else:
            LOG.debug(f'loadTexture({f_name}, {alpha_f_name})')

        # src/gobj/texturePool.cxx L:363-366
        if not self._fake_image.empty() \
           and (f_name != self._fake_image.getFullpath()):
            return self.loadTexture(
                self._fake_image,
                primary_file_num_channels = primary_file_num_channels,
                read_mipmaps = read_mipmaps,
                options = options)

        # src/gobj/texturePool.cxx L:368-374;206-210
        key = _CacheKey(
            self._resolveFilename(f_name, read_mipmaps, options),
            self._resolveFilename(alpha_f_name, read_mipmaps, options))

        # src/gobj/texturePool.cxx L:376-384;212-219
        if key in self._textures:
            # src/gobj/texturePool.cxx L:380-382;216-218
            tex = self._textures[key].texture
            assert not tex.getFullpath().empty()
            return tex
        # src/gobj/texturePool.cxx L:390-392;227-229
        else:
            # src/gobj/texturePool.cxx L:391;228
            # // Can one of our texture filters supply the texture?
            tex = self._preLoad(f_name, alpha_f_name,
                                primary_file_num_channels, alpha_file_channel,
                                read_mipmaps, options)
            if tex:
                return tex

            # src/gobj/texturePool.cxx L:388;225
            store_record = False
            # src/gobj/texturePool.cxx L:395-397;232-234
            record, tex, compressed = self._tryLoadCache(key.f_name, options)

            # // The texture was not supplied by a texture filter.
            # // See if it can be found in the on-disk cache, if it is active.
            # src/gobj/texturePool.cxx L:399-419;236-273
            # src/gobj/texturePool.cxx L:242
            ext = key.f_name.getExtension().lower()
            # src/gobj/texturePool.cxx L:243-272
            if ext in self.BAM_TYPES:
                # // Assume this is a txo file, which might conceivably
                # // contain a movie file or some other subclass of
                # // Texture. In that case, use make_from_txo() to load it
                # // instead of read().
                # src/gobj/texturePool.cxx L:249
                key.f_name.setBinary()
                # src/gobj/texturePool.cxx L:251-256
                f_obj = VFS.getFile(key.f_name)
                if not f_obj:
                    # // No such file.
                    LOG.warning(f'could not find: {key.f_name}')
                else:
                    # src/gobj/texturePool.cxx L:258-261
                    LOG.debug(f'reading texture object: {key.f_name}')

                    # src/gobj/texturePool.cxx L:263-265
                    data = f_obj.openReadFile(True)
                    path = key.f_name.getFullpath()
                    tex = p3d.Texture.makeFromTxo(data, path)
                    VFS.closeReadFile(data)

                    # src/gobj/texturePool.cxx L:270-272
                    if tex:
                        tex.setFullpath(key.f_name)
                        tex.clearAlphaFullpath()
                        tex.setKeepRamImage(False)
                    # src/gobj/texturePool.cxx L:267-269
                    else:
                        return None
            # src/gobj/texturePool.cxx L:274-282;400-411
            else:
                # // The texture was neither in the pool, nor found in
                # // the on-disk cache; it needs to be loaded from
                # // its src image(s).
                LOG.info(f'loading texture: {key.f_name}; '
                         f'alpha: {key.alpha_f_name}')
                # // Read it the conventional way.
                # src/gobj/texturePool.cxx L:276
                tex = self.makeTexture(ext)
                # src/gobj/texturePool.cxx L:277-282;406-412
                if not tex.read(key.f_name, key.alpha_f_name,
                                primary_file_num_channels,
                                alpha_file_channel, 0, 0, False,
                                read_mipmaps, None, options):
                    # src/gobj/texturePool.cxx L:279-280;409-410
                    # // This texture was not found or could not be read.
                    self._report(key.f_name)
                    return None
                # src/gobj/texturePool.cxx L:414-418
                else:
                    # src/gobj/texturePool.cxx L:414-416
                    if options.getTextureFlags() \
                       & p3d.LoaderOptions.TFPreloadSimple:
                        tex.generateSimpleRamImage()

                    # src/gobj/texturePool.cxx L:418;289
                    store_record = (record is not None)

            # src/gobj/texturePool.cxx L:421-439;292-310
            if self.CM_CompressCache and tex.hasCompression():
                # src/gobj/texturePool.cxx L:427-434;298-304
                if self.CM_DriverCompress:
                    # src/gobj/texturePool.cxx L:430-433;301-304
                    # // We don't want to save the uncompressed version; we'll
                    # // save the compressed version when it becomes available.
                    store_record = False
                    if not compressed:
                        tex.setPostLoadStoreCache(True)
            # src/gobj/texturePool.cxx L:436-439;307-310
            else:
                if not self.CM_Active:
                    # src/gobj/texturePool.cxx L:438;309
                    # // We don't want to save this texture.
                    store_record = False

            # src/gobj/texturePool.cxx L:441-447;312-316
            # // Set the original filenames, before we searched along the path.
            if tex:
                tex.setFilename(f_name)
                tex.setFullpath(key.f_name)
                tex.setAlphaFilename(alpha_f_name)
                tex.setAlphaFullpath(key.alpha_f_name)
            else:
                return None

            # src/gobj/texturePool.cxx L:452-460;321-330
            # // Now look again -- someone may have just loaded this
            # // texture in another thread.
            if key in self._textures:
                # src/gobj/texturePool.cxx L:457-459;326-329
                # // This texture was previously loaded.
                tex = self._textures[key].texture
                assert not tex.getFullpath().empty()
                return tex
            # src/gobj/texturePool.cxx L:462;332
            else:
                self._textures[key] = _CacheVal(
                    tex, primary_file_num_channels, alpha_file_channel)

            # src/gobj/texturePool.cxx L:465-469;335-339
            if store_record and tex.isCacheable():
                # Added this to handle the case where the cached texture
                # is compressed, but we are not caching compressed textures.
                # It's necessary to check because Texture.read calls
                # Texture.considerAutoProcessRamImage which auto-compresses
                # the texture if compressed-textures is set in the config.
                if self.isCompressed(tex) and not self.CM_CompressCache:
                    LOG.debug('uncompressing for cache')
                    tex.uncompressRamImage()

                # // Store the on-disk cache record for next time.
                LOG.debug(f'storing cache record: {key.f_name}')
                record.setData(tex)
                BAM.store(record)

                # And this to recompress the texture if we are compressing
                # everything in memory (compressed-textures).
                if self.CM_Compress and not self.isCompressed(tex):
                    LOG.debug('recompressing')
                    tex.compressRamImage()

            # src/gobj/texturePool.cxx L:471-474
            if not (options.getTextureFlags() & p3d.LoaderOptions.TFPreload):
                # // And now drop the RAM until we need it.
                tex.clearRamImage()

            # src/gobj/texturePool.cxx L:476;346
            assert not tex.getFullpath().empty()

            # src/gobj/texturePool.cxx L:478-481;348-351
            # // Finally, apply any post-loading texture filters.
            return self._postLoad(tex)

    # src/gobj/texturePool.I L:24-34
    def verifyTexture(self, f_name: p3d.Filename) -> bool:
        """
        /**
         * Loads the given filename up into a texture, if it has not already
         * been loaded, and returns true to indicate success, or false to
         * indicate failure. If this returns true, it is guaranteed that a
         * subsequent call to load_texture() with the same texture name will
         * return a valid Texture pointer.
         */
        """
        if not isinstance(f_name, p3d.Filename):
            LOG.warning('verifyTexture: f_name must be of type Filename')
            return False
        else:
            if self.loadTexture(f_name):
                return True
            else:
                return False
