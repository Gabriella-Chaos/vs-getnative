import os
import argparse
import vapoursynth


class GetnativeException(BaseException):
    pass


def vpy_source_filter(path):
    import runpy
    runpy.run_path(path, {}, "__vapoursynth__")
    if vapoursynth.core.version_number() < 55:
        return vapoursynth.get_output(0)
    else:
        return vapoursynth.get_output(0)[0]


def get_source_filter(core, imwri, args):
    ext = os.path.splitext(args.input_file)[1].lower()
    if imwri and (args.img or ext in {".png", ".tif", ".tiff", ".bmp", ".jpg", ".jpeg", ".webp", ".tga", ".jp2"}):
        print("Using imwri as source filter")
        return imwri.Read
    if ext in {".py", ".pyw", ".vpy"}:
        print("Using custom VapourSynth script as a source. This may cause garbage results. Only do this if you know what you are doing.")
        return vpy_source_filter

    source_filter = get_attr(core, 'bs.VideoSource')
    if source_filter:
        print("Using bs.VideoSource as source filter")
        return lambda input_file: source_filter(source=input_file)

    source_filter = get_attr(core, 'lsmas.LWLibavSource')
    if source_filter:
        print("Using lsmas.LWLibavSource as source filter")
        return source_filter

    source_filter = get_attr(core, 'ffms2.Source')
    if source_filter:
        print("Using ffms2 as source filter")
        return lambda input_file: source_filter(input_file, alpha=False)

    source_filter = get_attr(core, 'lsmas.LSMASHVideoSource')
    if source_filter:
        print("Using lsmas.LSMASHVideoSource as source filter")
        return source_filter

    raise GetnativeException("No source filter found.")


def get_attr(obj, attr, default=None):
    for ele in attr.split('.'):
        obj = getattr(obj, ele, default)
        if obj == default:
            return default
    return obj


def to_float(str_value):
    if set(str_value) - set("0123456789./"):
        raise argparse.ArgumentTypeError("Invalid characters in float parameter")
    try:
        return eval(str_value) if "/" in str_value else float(str_value)
    except (SyntaxError, ZeroDivisionError, TypeError, ValueError):
        raise argparse.ArgumentTypeError("Exception while parsing float") from None
