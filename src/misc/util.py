from chimerax.core.session import Session


def openable_suffixes(session: Session):
    formats = session.open_command.open_data_formats

    suffixes = []
    for fmt in formats:
        suffixes += fmt.suffixes

    return suffixes
