import itertools
from typing import Optional
from unittest import mock

import discord.embeds
import emoji
import pytest

from memebot import commands
from memebot.lib import constants, exception


async def do_poll_votes_test(
    mock_interaction: mock.Mock,
    expected_answers: list[str],
    yes_no: bool = False,
):
    """
    Tests that the vote buttons of a poll work properly
    """
    actual_view: discord.ui.View = (
        mock_interaction.response.send_message.call_args.kwargs.get("view")
    )
    initial_embed: discord.Embed = (
        mock_interaction.response.send_message.call_args.kwargs.get("embed")
    )

    assert actual_view is not None, "/poll did not create a view"

    # Assert that the number of buttons created is correct
    if yes_no:
        assert len(actual_view.children) == 2, "Didn't create 2 buttons for yes/no"
    else:
        assert len(actual_view.children) == len(
            expected_answers
        ), "Created wrong number of buttons"

    if yes_no:
        expected_emojis = ["👍", "👎"]
    else:
        expected_emojis = ["🇦", "🇧", "🇨", "🇩", "🇪"][: len(actual_view.children)]

    # Map button index -> number of expected votes
    votes = {k: 0 for k in range(len(expected_emojis))}

    # Function to generate embed fields based on the current voting
    def gen_fields():
        if yes_no:
            return [
                {
                    "name": f"{expected_emojis[k]} ({votes[k]})",
                    "value": "\n".join(u.display_name for u in mock_users[: votes[k]]),
                }
                for k in votes
            ]
        else:
            return [
                {
                    "name": f"{expected_emojis[k]} {expected_answers[k]} ({votes[k]})",
                    "value": "\n".join(u.display_name for u in mock_users[: votes[k]]),
                }
                for k in votes
            ]

    for i, button in enumerate(actual_view.children):
        assert isinstance(
            button, discord.ui.Button
        ), "/poll created non-button children"

        # Test that button attributes are correct
        assert button.emoji.name == expected_emojis[i]
        if yes_no:
            assert button.label is None, "Added extraneous label for yes/no button"
        else:
            assert button.label == expected_answers[i], "Button is mislabled"

        # Try voting 5 times
        n_votes = 5
        mock_users = []
        for j in range(n_votes):
            with mock.patch("discord.Member", spec=True) as MockMember:
                user = MockMember()
                user.display_name = str(j)
                mock_users.append(user)

        for vote_count in range(1, n_votes + 1):
            with mock.patch("discord.Interaction", spec=True) as MockInteraction:
                vote_interaction = MockInteraction()
                vote_interaction.response.edit_message = mock.AsyncMock()
                vote_interaction.user = mock_users[vote_count - 1]
                # Click a vote button
                await button.callback(vote_interaction)
            votes[i] += 1

            do_poll_embed_test(
                vote_interaction,
                initial_embed.description.strip("_"),
                gen_fields(),
                is_vote=True,
            )

        # Test un-voting
        for unvote_count in reversed(range(1, n_votes + 1)):
            with mock.patch("discord.Interaction", spec=True) as MockInteraction:
                vote_interaction = MockInteraction()
                vote_interaction.response.edit_message = mock.AsyncMock()
                vote_interaction.user = mock_users[unvote_count - 1]
                # Click a vote button
                await button.callback(vote_interaction)
            votes[i] -= 1

            do_poll_embed_test(
                vote_interaction,
                initial_embed.description.strip("_"),
                gen_fields(),
                is_vote=True,
            )


def do_poll_embed_test(
    mock_interaction: mock.Mock,
    question: str,
    expected_fields: list[dict[str, str]],
    is_vote: bool = False,
) -> None:
    """
    Tests that the embed for a poll is created correctly
    """

    if is_vote:
        expected_call = mock_interaction.response.edit_message
    else:
        expected_call = mock_interaction.response.send_message

    expected_call.assert_awaited_once()
    actual_embed: discord.Embed = expected_call.call_args.kwargs.get("embed")

    assert actual_embed is not None, "/poll did not send an embed"

    expected_title = ":bar_chart: **New Poll!**"
    expected_description = f"_{question}_"
    expected_color = constants.COLOR

    # Check embed attributes
    assert actual_embed.title == expected_title
    assert actual_embed.description == expected_description
    assert actual_embed.color == expected_color

    # Ensure all the desired choices are present and correctly ordered
    assert len(actual_embed.fields) == len(expected_fields)
    for actual, expected in zip(actual_embed.fields, expected_fields):
        proxy = discord.embeds.EmbedProxy(expected)
        assert actual.name == proxy.name
        assert actual.value == proxy.value


@pytest.mark.asyncio
async def test_poll_no_answers(mock_interaction: mock.Mock) -> None:
    """
    Test creation of a poll message with no answers as input. The poll message should
    contain the regular poll embed, with the only choices being automatically thumbs up
    and thumbs down.
    """
    question = "Mock question no args"
    await commands.poll.callback(mock_interaction, question, *[None] * 5)

    # Check that only 2 fields (positive, negative) were added to the embed
    expected_fields = [
        {"name": f"{emoji.emojize(':thumbs_up:')} (0)", "value": ""},
        {"name": f"{emoji.emojize(':thumbs_down:')} (0)", "value": ""},
    ]

    mock_interaction.response.send_message.assert_awaited_once()
    do_poll_embed_test(mock_interaction, question, expected_fields)
    await do_poll_votes_test(mock_interaction, [], yes_no=True)


@pytest.mark.parametrize(
    ["a1", "a2", "a3", "a4", "a5"],
    # Create a matrix of all possible answer inputs that contain only 1 real answer
    [
        ["Mock answer", None, None, None, None],
        [None, "Mock answer", None, None, None],
        [None, None, "Mock answer", None, None],
        [None, None, None, "Mock answer", None],
        [None, None, None, None, "Mock answer"],
    ],
)
@pytest.mark.asyncio
async def test_poll_one_answer(
    mock_interaction: mock.Mock,
    a1: Optional[str],
    a2: Optional[str],
    a3: Optional[str],
    a4: Optional[str],
    a5: Optional[str],
) -> None:
    """
    Test a poll with only one answer parameter provided. This is an illegal call and
    should result in an immediate throw without creating the poll
    """
    question = "Mock question 1 arg"
    with pytest.raises(exception.MemebotUserError):
        await commands.poll.callback(mock_interaction, question, a1, a2, a3, a4, a5)

    mock_interaction.response.send_message.assert_not_called()
    mock_interaction.original_response.assert_not_called()


def valid_answer_combinations() -> list[list[Optional[str]]]:
    """
    Generates a list of all possible valid answer configurations. The simple definition
    for a valid answer combination is any copy of ``mock_answers`` such that, at most,
    3 of the values are replaced with ``None``.
    """
    mock_answers = [
        "Mock answer 1",
        "Mock answer 2",
        "Mock answer 3",
        "Mock answer 4",
        "Mock answer 5",
    ]
    replace_max = 3
    return [
        [
            # 3. Generate an answer configuration by grabbing all the indexes from
            # mock_answers that we're not going to replace with None
            mock_answers[i] if i not in idxs_to_replace else None
            for i in range(len(mock_answers))
        ]
        # 1. Iterate through the number of replacements we can make
        for n_replacements in range(replace_max + 1)
        # 2. Iterate through all possible combinations of indices we can replace for
        # the n_replacements we're looking at
        for idxs_to_replace in itertools.combinations(
            range(len(mock_answers)), n_replacements
        )
    ]


@pytest.mark.parametrize(["a1", "a2", "a3", "a4", "a5"], valid_answer_combinations())
@pytest.mark.asyncio
async def test_poll_n_answers(
    mock_interaction: mock.Mock,
    a1: Optional[str],
    a2: Optional[str],
    a3: Optional[str],
    a4: Optional[str],
    a5: Optional[str],
) -> None:
    """
    Test a poll with any valid non-zero number of answers
    """
    possible_answers = [a1, a2, a3, a4, a5]
    question = f"Mock question with args: {possible_answers}"

    await commands.poll.callback(mock_interaction, question, *possible_answers)

    provided_answers = [a for a in possible_answers if a is not None]
    letter_emojis = ["🇦", "🇧", "🇨", "🇩", "🇪"]

    expected_fields = [
        {"name": f"{letter_emojis[i]} {answer} (0)", "value": ""}
        for i, answer in enumerate(provided_answers)
    ]

    do_poll_embed_test(mock_interaction, question, expected_fields)
    await do_poll_votes_test(mock_interaction, provided_answers)
