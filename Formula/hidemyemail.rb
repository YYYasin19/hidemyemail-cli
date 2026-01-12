class Hidemyemail < Formula
  include Language::Python::Virtualenv

  desc "CLI tool for managing Apple Hide My Email addresses with Touch ID"
  homepage "https://github.com/YYYasin19/hidemyemail-cli"
  license "MIT"

  # For development: install from local path or git
  # For release: replace with actual GitHub release URL
  head "https://github.com/YYYasin19/hidemyemail-cli.git", branch: "main"

  # Uncomment and update for stable releases:
  # url "https://github.com/YYYasin19/hidemyemail-cli/archive/refs/tags/v0.1.0.tar.gz"
  # sha256 "YOUR_SHA256_HERE"
  # version "0.1.0"

  depends_on "python@3.13"
  depends_on :macos  # Required for Touch ID and Keychain

  # Python dependencies
  resource "typer" do
    url "https://files.pythonhosted.org/packages/76/42/3efaf858001d2c2913de7f354563e3a3a2f0decae3efe98427125a8f441e/typer-0.15.1.tar.gz"
    sha256 "a0588c0a7fa68a1978a069818657778f86abe6ff5ea6abf472f940a08bfe4f0a"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/ab/3a/0316b28d0761c6734d6bc14e770d85506c986c85ffb239e688eebd274571/rich-13.9.4.tar.gz"
    sha256 "439594978a49a09530cff7ebc4b5c7103ef57c74805e1a3be8cb06c5229cde21"
  end

  resource "shellingham" do
    url "https://files.pythonhosted.org/packages/58/15/8b3609fd3830ef7b27b655beb4b4e9c62313a4e8da8c676e142cc210d58e/shellingham-1.5.4.tar.gz"
    sha256 "8dbca0739d487e5bd35ab3ca4b36e11c4078f3a234bfce294b0a0291363404de"
  end

  resource "click" do
    url "https://files.pythonhosted.org/packages/96/d3/f04c7bfcf5c1862a2a5b845c6b2b360488cf47af55dfa79c98f6a6bf98b5/click-8.1.7.tar.gz"
    sha256 "ca9853ad459e787e2192211578cc907e7594e294c7ccc834310722b41b9ca6de"
  end

  resource "markdown-it-py" do
    url "https://files.pythonhosted.org/packages/38/71/3b932df36c1a044d397a1f92d1cf91ee0a503d91e470cbd670aa66b07571/markdown-it-py-3.0.0.tar.gz"
    sha256 "e3f60a94fa066dc52ec76661e37c851cb232d92f9886b15cb560aaada2df8feb"
  end

  resource "mdurl" do
    url "https://files.pythonhosted.org/packages/d6/54/cfe61301667036ec958cb99bd3ead613a0d4ab03bce2e5e78e5e8efda293/mdurl-0.1.2.tar.gz"
    sha256 "bb413d29f5eea38f31dd4754dd7377d4465116fb207585f97bf925588687c1ba"
  end

  resource "pygments" do
    url "https://files.pythonhosted.org/packages/7c/2d/c3338d48ea6cc0feb8446d8e6937e1408088a72a39937982cc6111d17f84/pygments-2.19.1.tar.gz"
    sha256 "61c16d2a8576dc0649d9f39e089b5f02bcd27fba10d8fb4dcc28173f7a45151f"
  end

  resource "typing-extensions" do
    url "https://files.pythonhosted.org/packages/df/db/f35a00659bc03fec321ba8bce9420de607a1d37f8342eee1863174c69557/typing_extensions-4.12.2.tar.gz"
    sha256 "1a7ead55c7e559dd4dee8856e3a88b41225abfe1ce8df57b7c13915fe121ffb8"
  end

  # pyobjc dependencies
  resource "pyobjc-core" do
    url "https://files.pythonhosted.org/packages/6b/c4/f6c0d09d581620c547c7cd4e3d6307e78f2de63f5a10f968bda96e04944a/pyobjc_core-10.3.2.tar.gz"
    sha256 "e7feb76e4a4117cd54f0af6a4e554b00af4c6dd01597a02c396e3f758b469c66"
  end

  resource "pyobjc-framework-Cocoa" do
    url "https://files.pythonhosted.org/packages/7c/7b/dd10f3c0e0c13864f20fe63f11b17a79d786c9b6dcd0a9aa095e1e1a8770/pyobjc_framework_cocoa-10.3.2.tar.gz"
    sha256 "372bc3e6ea56e933c2edfe6083bee1d3c9c0f97bb1e00c2836a5d70ea152e087"
  end

  resource "pyobjc-framework-LocalAuthentication" do
    url "https://files.pythonhosted.org/packages/9c/8b/4207e3db2fa50376ef0e1efb3a1f98a8ad2a4db423a98fc9e2ea40c09c7f/pyobjc_framework_localauthentication-10.3.2.tar.gz"
    sha256 "8dc0f05fa8e8e49eca6b1c922fdcfe98e8d24f8a1cc3b8693e0961ed619ce813"
  end

  resource "pyobjc-framework-Security" do
    url "https://files.pythonhosted.org/packages/ac/8b/04d07b68d6adab84a0e81e6f2a8ea4c8bb7ea7c5afca7dab96d0333f6eb6/pyobjc_framework_security-10.3.2.tar.gz"
    sha256 "b3c0cfd6dce4f38f26c376ae6e6e4dc67c2a88d4c0d33f59b61c96fd4e4dcf9c"
  end

  # pyicloud from timlaing fork (has Hide My Email support)
  resource "pyicloud" do
    url "https://github.com/timlaing/pyicloud/archive/refs/heads/master.tar.gz"
    sha256 :no_check  # GitHub archives don't have stable SHA
  end

  # pyicloud dependencies
  resource "requests" do
    url "https://files.pythonhosted.org/packages/63/70/2bf7780ad2d390a8d301ad0b550f1581eadbd9a20f896afe06353c2a2913/requests-2.32.3.tar.gz"
    sha256 "55365417734eb18255590a9ff9eb97e9e1da868d4ccd6402399eaf68af20a760"
  end

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/0f/bd/1d41ee578ce09523c81a15426705dd20969f5abf006d1afe8aeff0dd776a/certifi-2024.12.14.tar.gz"
    sha256 "b650d30f370c2b724812bee08008be0c4163b163ddaec3f2546c1caf65f191db"
  end

  resource "charset-normalizer" do
    url "https://files.pythonhosted.org/packages/f2/4f/e1808dc01273379acc506d18f1504eb2ac0d1de2e5e67ee02fa4735bc748/charset_normalizer-3.4.1.tar.gz"
    sha256 "44251f18cd68a75b56585dd00dae26183e102cd5e0f9f1466e6df5da2ed64ea3"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/f1/70/7703c29685631f5a7590aa73f1f1d3fa9a380e654b86af429e0934a32f7d/idna-3.10.tar.gz"
    sha256 "12f65c9b470abda6dc35cf8e63cc574b1c52b11df2c86030af0ac09b01b13ea9"
  end

  resource "urllib3" do
    url "https://files.pythonhosted.org/packages/aa/63/e53da845320b757bf29ef6a9062f5c669f8dc6e321d7ffb5d91bc5cf9a14/urllib3-2.3.0.tar.gz"
    sha256 "f8c5449b3cf0861679ce7e0503c7b44b5ec981bec0d1d3795a07f1ba96f0c824"
  end

  resource "keyring" do
    url "https://files.pythonhosted.org/packages/70/09/d904a6e96f76ff214be59e7aa6ef7190b4b64371e97f82e3e3bfa18315f0/keyring-25.5.0.tar.gz"
    sha256 "4c753b3ec91717fe713c4edd522571571d606c4ea3b439e3a25df2c622102a20"
  end

  resource "jaraco-classes" do
    url "https://files.pythonhosted.org/packages/06/c0/ed4a27bc5571b99e3cff68f8a9fa5b56ff7df1c2251cc715a652ddd26402/jaraco.classes-3.4.0.tar.gz"
    sha256 "47a024b51d0239c0dd8c8540c6c7f484be3b8fcf0b2d85c13825780d3b3f3acd"
  end

  resource "jaraco-functools" do
    url "https://files.pythonhosted.org/packages/ab/23/9894b3df5571a89c6dc2c577b2dfafa88ee6a5e94a5e0fc34f6f2a2e6f02/jaraco_functools-4.1.0.tar.gz"
    sha256 "70f7e0306a754f90e26056f1d49faec3b5a34c7e7a85dfaf46fb4bad2fe9d5bd"
  end

  resource "jaraco-context" do
    url "https://files.pythonhosted.org/packages/df/ad/f3777b81bf0b6e7bc7514a1656d3e637b2e8e15fab2ce3235730b3e7a4e6/jaraco_context-6.0.1.tar.gz"
    sha256 "9bae4ea555cf0b14938dc0aee7c9f32ed303aa20a3b73e7dc80111628792d1b3"
  end

  resource "more-itertools" do
    url "https://files.pythonhosted.org/packages/51/78/65922308c4248e0eb08ebcbe67c95f3b153ebbe4a36e5d9d2628c40f4278/more_itertools-10.5.0.tar.gz"
    sha256 "037b0d3203ce90cca8ab1defbbdac29d5f993fc20131f3664dc8d6acfa872aef"
  end

  resource "tzlocal" do
    url "https://files.pythonhosted.org/packages/04/d3/c19d65ae67636fe63953b20c2e4a8ced4497ea232c43571f733a4a3fba42/tzlocal-5.2.tar.gz"
    sha256 "8d399205578f1a9342816409cc1e46a93ebd5755e39ea2d85334bea911bf0e6e"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "hme version", shell_output("#{bin}/hme --version")
  end
end
