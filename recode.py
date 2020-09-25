from __future__ import annotations

from abc import abstractmethod
from collections import UserList, namedtuple
import re
from typing import Any, Protocol, List, Optional, Tuple

from anytree import NodeMixin, RenderTree


Patterns = namedtuple('Patterns', ['line', 'group', 'range'])

# Recodes table patterns:

CODE_INTEGER = r'\s*(\d+)'
CODE_ICD_10 = r'\s*(?:\*)?(\w\d\d\.?\d?)'
RANGE_ICD_10 = fr'{CODE_ICD_10}\s*(?:-{CODE_ICD_10})?'
GROUP_ICD_10 = fr'(?:{RANGE_ICD_10}(?:,)?)+'

ICD_10_TO_INTEGER = Patterns(
    line=fr'{CODE_INTEGER}\s*=.+\(({GROUP_ICD_10})\)\s*$',
    group=GROUP_ICD_10,
    range=RANGE_ICD_10,
)


class Comparable(Protocol):
    """Represents a comparable object, i.e. each 2 Comparable objects return bool with < and >."""
    @abstractmethod
    def __lt__(self, other: Any) -> bool: pass

    @abstractmethod
    def __gt__(self, other: Any) -> bool: pass

    def __le__(self, other: Any) -> bool:
        return not self > other

    def __ge__(self, other: Any) -> bool:
        return not self < other


# A code has to be comparable.
Code = Comparable


class CodeRange:
    """Represents a range of codes."""
    def __init__(self, start: Code, end: Optional[Code]):
        """Create CodeRange.

        :param start: the first code in the range
        :param end: the last code in the range
        """
        self.start = start
        self.end = end if end else self.start

    def __repr__(self) -> str:
        suffix = f'-{self.end}' if self.end != self.start else ''
        return f'{self.start}{suffix}'

    def __contains__(self, code_range: CodeRange) -> bool:
        """Check if this code range contains *code_range*.

        :param code_range: code_range, e.g. A01-A10 or C01
        :return: True if and only if this code range contains *code_range*, e.g. A01-B99 contains A01-A10
        """
        return self.start <= code_range.start <= code_range.end <= self.end


class Group(UserList):
    def __init__(self, group: List[CodeRange]):
        """Create Group

        :param group: List of CodeRange
        """
        super().__init__(group)

    def __contains__(self, code_range: CodeRange) -> bool:
        """Check if this Group contains *code_range*.

        :param code_range: range of codes, e.g. A01-A10
        :return: True if and only if this Group contain *code_range*, e.g. [A01-B99, C01-C99] contains A01-A10
        """
        return any([
            code_range in other_code_range
            for other_code_range in self.data
        ])


class RecodeNode(NodeMixin):
    """A tree node that represents a recode and its hierarchy."""
    def __init__(self, code: Code, group: Group, parent: RecodeNode = None):
        """Initialize a Recode Node.

        :param code: the new code
        :param group: the group of codes that *code* represents
        :param parent: parent of this Recode
        """
        super().__init__()
        self.code = code
        self.group = group
        self.parent = parent

    def __repr__(self):
        return f'{self.code} = {self.group}'

    def __contains__(self, group: Group) -> bool:
        """Check if this Recode contains *group*.

        :param group: group of codes, e.g. [A01-A10, C90-C99]
        :return: True if and only if this Recode contains ranges,
            e.g. self.group=[A01-B99, C01-C99] contains [A01-A10, C90-C99]
        """
        return all([code_range in self.group for code_range in group])

    def get_path(self, group: Group) -> List[RecodeNode]:
        """Return list of all nodes that contain *group*.

        :param group: group of codes, e.g. [A01-A10, C90-C99]
        :return: list of all codes of *group*
        """
        for child in self.children:
            if group in child:
                return [child, *child.get_path(group)]
        else:
            return []


class Recoder:
    """Converter from one coding system another.

    Quick start:
        from recode import Recoder
        recoder = Recoder('tables/358 ICD-10 Recodes.txt')
        print(recoder)
        print(recoder.get_codes('G20'))
    """
    FilePath = str

    def __init__(self, file: FilePath, patterns: Patterns = ICD_10_TO_INTEGER):
        """Stores *recodes* in a tree structure for fast access.

        :param file: a text file that contains a Recodes Table
        :param patterns: patterns of each recode line; default is the following:
            recode = description (group of codes in ranges or singular),
            e.g. '	07400 = Of pharynx (C10-C13, C14.0)'
        """
        self.patterns = patterns
        self.root = RecodeNode(0, Group([CodeRange('A99', 'Z99')]))
        with open(file) as lines:
            next(lines)  # Skip header line
            for line in lines:
                if line_match := re.search(self.patterns.line, line):
                    new_code = line_match[1]
                    group = self.create_group(line_match[2])
                    parent_recode = [self.root, *self.root.get_path(group)][-1]
                    RecodeNode(new_code, group, parent=parent_recode)
                else:
                    raise ValueError(f'Line {line.strip()!r} is not valid')

    def __str__(self) -> str:
        """Return a tree representation of all the codes."""
        return str(RenderTree(self.root))

    def get_codes(self, group: str) -> list:
        """Return list of all codes that match *group*.

        :param group: group of codes, e.g. 'A01-A10, C90-C99'
            The group contains one or more range of codes, each range can be singular (G20 <=> G20-G20)
        :return: list of all codes that match *group*
        """
        if not re.fullmatch(self.patterns.group, group):
            raise ValueError(f'Group {group!r} is not valid')
        return [node.code for node in self.root.get_path(self.create_group(group))]

    def create_group(self, group: str) -> Group:
        """Return new Group based on *group*.

        :param group: group of codes, e.g. 'A01-A10, C90-C99'
            The group contains one or more range of codes, each range can be singular (G20 <=> G20-G20)
        :return: appropriate Group object
        """
        range_iter = re.finditer(self.patterns.range, group)
        return Group([
            CodeRange(*self.preprocess_range(range_match[1], range_match[2]))
            for range_match in range_iter
        ])

    def preprocess_range(self, start: str, end: str) -> Tuple[str, str]:
        if self.patterns.range == RANGE_ICD_10:
            if start:
                if len(start) == 3:
                    start += '.0'
                elif start[3] != '.':
                    start = '.'.join([start[:3], start[3:]])
            if end:
                if len(end) == 3:
                    end += '.9'
                elif end[3] != '.':
                    end = '.'.join([end[:3], end[3:]])

        return start, end
